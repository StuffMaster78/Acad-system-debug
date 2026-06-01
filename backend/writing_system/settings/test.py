"""
writing_system/settings/test.py
────────────────────────────────────────────────────────────────────────────────
Test environment settings. Fast DB, no external services.
────────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

from .base import *  # noqa: F401,F403
from .env import env


DJANGO_ENV = "test"
DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"
TOKEN_ENCRYPTION_KEY = env(
    "TOKEN_ENCRYPTION_KEY",
    "test-token-encryption-key",
)
FIELD_ENCRYPTION_KEY = env(
    "FIELD_ENCRYPTION_KEY",
    "test-field-encryption-key",
)


database_url = os.getenv("DATABASE_URL")
test_db = os.getenv("TEST_DB", "sqlite").lower()

if database_url:
    parsed = urlparse(database_url)
    db_name = parsed.path[1:] if parsed.path.startswith("/") else parsed.path
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
            "USER": parsed.username,
            "PASSWORD": parsed.password,
            "HOST": parsed.hostname,
            "PORT": parsed.port or 5432,
            "TEST": {
                "NAME": f"test_{db_name}",
                "CREATE_DB": True,
            },
        },
    }
elif test_db == "postgres":
    _db_name = os.getenv("POSTGRES_DB_NAME") or "writing_system_db"
    _db_host = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "localhost"
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": os.getenv("POSTGRES_USER_NAME") or "postgres",
            "PASSWORD": os.getenv("POSTGRES_PASSWORD") or "postgres",
            "HOST": _db_host,
            "PORT": int(os.getenv("DB_PORT", 5432)),
            "TEST": {
                "NAME": f"test_{_db_name}",
                "CREATE_DB": True,
            },
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        },
    }

    class DisableMigrations(dict):
        """
        Tell Django to sync models directly for local SQLite tests.
        """

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()


CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core.middleware.portal_tenant_resolver.PortalTenantResolverMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SENTRY_DSN = ""
STORAGE_BACKEND = "local"
USE_S3 = False
MEDIA_ROOT = "/tmp/writing-system-test-media/"

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

for _app in [
    "drf_spectacular_sidecar",
    "django_ratelimit",
]:
    if _app in INSTALLED_APPS:  # noqa: F405
        INSTALLED_APPS.remove(_app)  # noqa: F405

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "notifications_write_burst": "1000/min",
        "notifications_read_burst": "1000/min",
        "notifications_write_sustained": "10000/day",
        "notifications_read_sustained": "10000/day",
        "user": "1000/min",
        "anon": "1000/min",
    },
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
}

SILENCED_SYSTEM_CHECKS = [
    "notifications_system.E011",
    "django_ratelimit.E003",
    "admin.E035",
    "fields.E304",
    "fields.E305",
    "fields.E300",
    "fields.E307",
    "urls.W005",
    "notifications_system.W001",
    "notifications_system.W026",
]

DISABLE_AUDIT_LOG_SIGNALS = True
DISABLE_NOTIFICATION_SIGNALS = True
DISABLE_SUPPORT_SIGNALS = True
DISABLE_REFERRAL_SIGNALS = True
DISABLE_COMMUNICATION_EVENTS = True
DISABLE_PRICE_RECALC_DURING_TESTS = True
DISABLE_AUTO_CREATE_WRITER_PROFILE = True

ALLOWED_HOSTS = ["*"]  # tests use arbitrary tenant hostnames
