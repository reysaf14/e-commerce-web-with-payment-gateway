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
