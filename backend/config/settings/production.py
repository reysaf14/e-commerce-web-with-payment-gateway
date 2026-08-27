"""
Production settings — uses MySQL from .env.
"""

from .base import *  # noqa: F401,F403
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# ── Security guard: production MUST have real secrets ─────
if not MIDTRANS_SERVER_KEY:
    raise ImproperlyConfigured(
        "MIDTRANS_SERVER_KEY wajib diisi di .env untuk production "
        "(server key asli, bukan placeholder)."
    )

# ── Database: MySQL ────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME", default="ecommerce_fashion"),
        "USER": env("DB_USER", default="root"),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default=3306),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ── Security ───────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# ── Email: SMTP ───────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD", default="")
