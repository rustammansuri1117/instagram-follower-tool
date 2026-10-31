from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from extensions import db
from models import Order, Plan, User
from utils import clean_mobile, clean_username, validate_order

user_bp = Blueprint("user", __name__)


def _get_active_plan(plan_id):
    plan = db.session.get(Plan, plan_id)
    if plan is None or not plan.is_active:
        abort(404)
    return plan


@user_bp.route("/order/<int:plan_id>")
def order_form(plan_id):
    return render_template("order.html", plan=_get_active_plan(plan_id), form={})


@user_bp.route("/submit-order", methods=["POST"])
def submit_order():
    try:
        plan = _get_active_plan(int(request.form.get("plan_id", "")))
    except ValueError:
        abort(400)

    username = clean_username(request.form.get("instagram_username"))
    mobile = clean_mobile(request.form.get("mobile_number"))
    errors = validate_order(username, mobile)
    if errors:
        for message in errors:
            flash(message, "danger")
        form = {"instagram_username": username, "mobile_number": mobile}
        return render_template("order.html", plan=plan, form=form), 400

    user = User.query.filter_by(instagram_username=username, mobile_number=mobile).first()
    if user is None:
        user = User(instagram_username=username, mobile_number=mobile)
        db.session.add(user)
    order = Order(user=user, plan=plan, amount=plan.price)  # price always read from the DB
    db.session.add(order)
    db.session.commit()

    mine = session.get("my_orders", [])
    session["my_orders"] = (mine + [order.id])[-10:]
    return redirect(url_for("user.confirmation", order_id=order.id))


@user_bp.route("/confirmation/<int:order_id>")
def confirmation(order_id):
    if order_id not in session.get("my_orders", []):
        flash("Use Track Order with your order ID and mobile number to view an order.", "info")
        return redirect(url_for("main.track_order"))
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)
    return render_template("confirmation.html", order=order)
