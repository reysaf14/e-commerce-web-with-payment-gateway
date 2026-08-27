"""
Development settings — uses SQLite for local dev (no MySQL required).
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ── Database: SQLite for local dev ─────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── Email: console backend (prints to terminal) ───────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Midtrans (dev only): seed key untuk pengujian lokal ───
# Gunakan key sandbox asli dari .env kalau mau tes bayar nyata.
MIDTRANS_SERVER_KEY = env("MIDTRANS_SERVER_KEY", default="dev-local-test-key-not-for-production")
MIDTRANS_CLIENT_KEY = env("MIDTRANS_CLIENT_KEY", default="dev-local-client-key")
