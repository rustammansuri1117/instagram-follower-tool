from flask import Blueprint, flash, render_template, request

from extensions import db
from models import Order, Plan
from utils import clean_mobile

main_bp = Blueprint("main", __name__)


def active_plans():
    return Plan.query.filter_by(is_active=True).order_by(Plan.follower_quantity).all()


@main_bp.route("/")
def index():
    return render_template("index.html", plans=active_plans())


@main_bp.route("/plans")
def plans():
    return render_template("plans.html", plans=active_plans())


@main_bp.route("/track-order", methods=["GET", "POST"])
def track_order():
    order = None
    if request.method == "POST":
        order_id = (request.form.get("order_id") or "").strip().lstrip("#")
        mobile = clean_mobile(request.form.get("mobile_number"))
        if order_id.isdigit() and len(order_id) < 10:
            candidate = db.session.get(Order, int(order_id))
            if candidate and candidate.user.mobile_number == mobile:
                order = candidate
        if order is None:  # same message either way, so IDs can't be probed
            flash("We couldn't find an order matching that ID and mobile number.", "warning")
    return render_template("tracking.html", order=order)
