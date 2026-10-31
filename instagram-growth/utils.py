import re
from decimal import Decimal, InvalidOperation

USERNAME_RE = re.compile(r"^(?!\.)(?!.*\.\.)[A-Za-z0-9._]{1,30}$")
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")


def clean_username(raw):
    return (raw or "").strip().lstrip("@").lower()


def clean_mobile(raw):
    digits = re.sub(r"[\s\-()]", "", raw or "")
    if digits.startswith("+91"):
        digits = digits[3:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    return digits


def validate_order(username, mobile):
    errors = []
    if not USERNAME_RE.match(username):
        errors.append("Enter a valid Instagram username (letters, numbers, periods and underscores, up to 30 characters).")
    if not MOBILE_RE.match(mobile):
        errors.append("Enter a valid 10-digit Indian mobile number.")
    return errors


def parse_plan_form(form):
    """Return (data, errors) for the admin plan form."""
    errors = []
    name = (form.get("plan_name") or "").strip()
    if not 1 <= len(name) <= 100:
        errors.append("Plan name is required (max 100 characters).")
    try:
        qty = int(form.get("follower_quantity", ""))
        if not 1 <= qty <= 10_000_000:
            raise ValueError
    except ValueError:
        qty = None
        errors.append("Follower quantity must be a whole number between 1 and 10,000,000.")
    try:
        price = Decimal(form.get("price", "")).quantize(Decimal("0.01"))
        if not Decimal("0.01") <= price <= Decimal("1000000"):
            raise ValueError
    except (InvalidOperation, ValueError):
        price = None
        errors.append("Price must be a number greater than 0.")
    data = {
        "plan_name": name,
        "follower_quantity": qty,
        "price": price,
        "is_active": form.get("is_active") == "on",
    }
    return data, errors
