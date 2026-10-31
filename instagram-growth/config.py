import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def _db_uri():
    override = os.getenv("DATABASE_URL")  # optional full URI override (e.g. for tests)
    if override:
        return override
    user = quote_plus(os.getenv("DB_USER", "root"))
    pwd = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "instagram_growth_db")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-only-insecure-key"
    SQLALCHEMY_DATABASE_URI = _db_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    WTF_CSRF_TIME_LIMIT = 3600 * 4
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "support@example.com")
    CONTACT_PHONE = os.getenv("CONTACT_PHONE", "+91 00000 00000")
