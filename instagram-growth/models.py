from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

ORDER_STATUSES = ["Pending", "Processing", "Completed", "Cancelled"]
PAYMENT_STATUSES = ["Unpaid", "Paid"]


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    instagram_username = db.Column(db.String(30), nullable=False, index=True)
    mobile_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("instagram_username", "mobile_number", name="uq_user_identity"),
    )


class Plan(db.Model):
    __tablename__ = "plans"
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    follower_quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    orders = db.relationship("Order", back_populates="plan")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # price locked at order time
    order_status = db.Column(db.String(20), default="Pending", nullable=False, index=True)
    payment_status = db.Column(db.String(10), default="Unpaid", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    user = db.relationship("User", back_populates="orders")
    plan = db.relationship("Plan", back_populates="orders")
