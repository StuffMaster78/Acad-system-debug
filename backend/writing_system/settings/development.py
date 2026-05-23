from __future__ import annotations

from .base import *  # noqa: F401,F403
from .env import env, env_bool, env_int, env_list


DJANGO_ENV = "development"
DEBUG = True

ALLOWED_HOSTS = env_list(  # noqa: F405
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,testserver",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB_NAME", "writingsondo"),
        "USER": env("POSTGRES_USER_NAME", "postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", "postgres"),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env_int("DB_PORT", 5432),
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {
            "connect_timeout": env_int("DB_CONNECT_TIMEOUT", 10),
        },
    },
}

CORS_ALLOW_ALL_ORIGINS = env_bool(  # noqa: F405
    "CORS_ALLOW_ALL_ORIGINS",
    False,
)

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

STORAGE_BACKEND = env("STORAGE_BACKEND", "local")
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

SILENCED_SYSTEM_CHECKS = [
    *SILENCED_SYSTEM_CHECKS,  # noqa: F405
    "notifications_system.W001",
]
