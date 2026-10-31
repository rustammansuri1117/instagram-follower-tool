from time import time

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_

from extensions import db
from models import ORDER_STATUSES, PAYMENT_STATUSES, Admin, Order, Plan, User
from utils import parse_plan_form

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

_failed = {}  # ip -> [timestamps]; simple in-process brute-force throttle
MAX_FAILS, WINDOW = 5, 600


def _throttled(ip):
    now = time()
    _failed[ip] = [t for t in _failed.get(ip, []) if now - t < WINDOW]
    return len(_failed[ip]) >= MAX_FAILS


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        ip = request.remote_addr or "?"
        if _throttled(ip):
            flash("Too many failed attempts. Try again in a few minutes.", "danger")
            return render_template("admin/login.html"), 429
        admin = Admin.query.filter_by(username=(request.form.get("username") or "").strip()).first()
        if admin and admin.check_password(request.form.get("password") or ""):
            _failed.pop(ip, None)
            login_user(admin)
            return redirect(url_for("admin.dashboard"))
        _failed.setdefault(ip, []).append(time())
        flash("Invalid username or password.", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    count = lambda *f: db.session.query(func.count(Order.id)).filter(*f).scalar()
    revenue = (
        db.session.query(func.coalesce(func.sum(Order.amount), 0))
        .filter(Order.payment_status == "Paid", Order.order_status != "Cancelled")
        .scalar()
    )
    stats = {
        "users": db.session.query(func.count(User.id)).scalar(),
        "orders": count(),
        "pending": count(Order.order_status == "Pending"),
        "completed": count(Order.order_status == "Completed"),
        "revenue": revenue,
    }
    recent = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@admin_bp.route("/orders")
@login_required
def orders():
    status = request.args.get("status", "")
    search = (request.args.get("q") or "").strip()[:60]
    page = request.args.get("page", 1, type=int)

    query = Order.query.join(User).join(Plan)
    if status in ORDER_STATUSES:
        query = query.filter(Order.order_status == status)
    if search:
        like = f"%{search}%"
        conds = [User.instagram_username.ilike(like), User.mobile_number.like(like)]
        if search.lstrip("#").isdigit():
            conds.append(Order.id == int(search.lstrip("#")))
        query = query.filter(or_(*conds))
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template("admin/orders.html", pagination=pagination, status=status, q=search,
                           statuses=ORDER_STATUSES, payment_statuses=PAYMENT_STATUSES)


@admin_bp.route("/update-status/<int:order_id>", methods=["POST"])
@login_required
def update_status(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)
    status = request.form.get("order_status")
    payment = request.form.get("payment_status")
    if status not in ORDER_STATUSES or payment not in PAYMENT_STATUSES:
        abort(400)
    order.order_status, order.payment_status = status, payment
    db.session.commit()
    flash(f"Order #{order.id} updated: {status}, {payment}.", "success")
    return redirect(url_for("admin.orders", status=request.form.get("filter_status", ""),
                            q=request.form.get("filter_q", ""), page=request.form.get("page", 1, type=int)))


@admin_bp.route("/users")
@login_required
def users():
    search = (request.args.get("q") or "").strip()[:60]
    query = db.session.query(User, func.count(Order.id)).outerjoin(Order).group_by(User.id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(User.instagram_username.ilike(like), User.mobile_number.like(like)))
    rows = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", rows=rows, q=search)


@admin_bp.route("/plans")
@login_required
def plans():
    return render_template("admin/plans.html", plans=Plan.query.order_by(Plan.follower_quantity).all())


@admin_bp.route("/plans/add", methods=["POST"])
@login_required
def add_plan():
    data, errors = parse_plan_form(request.form)
    if errors:
        for e in errors:
            flash(e, "danger")
    else:
        db.session.add(Plan(**data))
        db.session.commit()
        flash("Plan added.", "success")
    return redirect(url_for("admin.plans"))


@admin_bp.route("/plans/<int:plan_id>/edit", methods=["POST"])
@login_required
def edit_plan(plan_id):
    plan = db.session.get(Plan, plan_id)
    if plan is None:
        abort(404)
    data, errors = parse_plan_form(request.form)
    if errors:
        for e in errors:
            flash(e, "danger")
    else:
        for key, value in data.items():
            setattr(plan, key, value)
        db.session.commit()
        flash("Plan updated. Existing orders keep the price they were placed at.", "success")
    return redirect(url_for("admin.plans"))


@admin_bp.route("/plans/<int:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):
    plan = db.session.get(Plan, plan_id)
    if plan is None:
        abort(404)
    if plan.orders:
        plan.is_active = False
        flash("This plan has orders, so it was deactivated instead of deleted.", "info")
    else:
        db.session.delete(plan)
        flash("Plan deleted.", "success")
    db.session.commit()
    return redirect(url_for("admin.plans"))
