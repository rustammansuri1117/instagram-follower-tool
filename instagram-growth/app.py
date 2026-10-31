import os
import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import csrf, db, login_manager
from models import Admin, Plan


DEFAULT_PLANS = [
    ("500 Followers", 500, 99),
    ("1K Followers", 1000, 199),
    ("5K Followers", 5000, 499),
    ("10K Followers", 10000, 899),
]


def seed_plans():
    if Plan.query.count() == 0:
        for name, qty, price in DEFAULT_PLANS:
            db.session.add(Plan(plan_name=name, follower_quantity=qty, price=price))
        db.session.commit()


def seed_admin_from_env():
    admin_user = (os.getenv("ADMIN_USERNAME") or "").strip()
    admin_pass = os.getenv("ADMIN_PASSWORD") or ""
    if admin_user and len(admin_pass) >= 8:
        admin = Admin.query.filter_by(username=admin_user).first()
        if admin is None:
            admin = Admin(username=admin_user)
            db.session.add(admin)
        admin.set_password(admin_pass)
        db.session.commit()


def register_filters(app):
    @app.template_filter("inr")
    def inr(value):
        value = float(value)
        return f"₹{value:,.0f}" if value == int(value) else f"₹{value:,.2f}"

    @app.template_filter("dt")
    def dt(value):  # stored as UTC, shown in IST
        return (value + timedelta(hours=5, minutes=30)).strftime("%d %b %Y, %I:%M %p IST")

    @app.template_filter("status_class")
    def status_class(value):
        return {"Pending": "warning", "Processing": "info", "Completed": "success",
                "Cancelled": "secondary", "Paid": "success", "Unpaid": "danger"}.get(value, "secondary")


def register_errors(app):
    def render_error(code, title, message):
        return render_template("error.html", code=code, title=title, message=message), code

    @app.errorhandler(400)
    def bad_request(e):
        return render_error(400, "Bad request", "We couldn't process that request.")

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return render_error(400, "Session expired", "Your form session expired. Go back, refresh the page, and try again.")

    @app.errorhandler(403)
    def forbidden(e):
        return render_error(403, "Access denied", "You don't have permission to view this page.")

    @app.errorhandler(404)
    def not_found(e):
        return render_error(404, "Page not found", "The page you're looking for doesn't exist.")

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_error(500, "Something went wrong", "An unexpected error occurred. Please try again later.")


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, password):
        """Create (or reset the password of) an admin account."""
        username = username.strip()
        if len(password) < 8:
            raise click.ClickException("Password must be at least 8 characters.")
        admin = Admin.query.filter_by(username=username).first()
        if admin is None:
            admin = Admin(username=username)
            db.session.add(admin)
        admin.set_password(password)
        db.session.commit()
        click.echo(f"Admin '{username}' is ready.")

    @app.cli.command("init-db")
    def init_db():
        """Create tables and seed the default plans."""
        db.create_all()
        seed_plans()
        click.echo("Database initialised.")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Please log in to access the admin area."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    from routes.admin import admin_bp
    from routes.main import main_bp
    from routes.user import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    register_filters(app)
    register_errors(app)
    register_cli(app)

    @app.context_processor
    def inject_contact():
        return {"contact_email": app.config["CONTACT_EMAIL"], "contact_phone": app.config["CONTACT_PHONE"]}

    with app.app_context():
        try:
            db.create_all()
            seed_plans()
            seed_admin_from_env()
        except SQLAlchemyError as exc:
            app.logger.error("Database not ready - check database settings and your .env file: %s", exc)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
