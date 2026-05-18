from .base import *
import os
from datetime import timedelta

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB_NAME"),
        "USER": os.getenv("POSTGRES_USER_NAME"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", 5432),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", 600)),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Celery broker (production only)
CELERY_BROKER_URL = _redis_url(0)
CELERY_RESULT_BACKEND = _redis_url(0)

# Storage backend stays production-safe
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "s3")

# Sentry (optional)
SENTRY_DSN = os.getenv("SENTRY_DSN")