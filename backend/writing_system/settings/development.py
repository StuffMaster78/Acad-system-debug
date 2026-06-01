from __future__ import annotations

"""
Development overrides. Never deploy these settings to production.
"""

from .base import * # noqa: F401,F403
from .base import module_available # explicit import so it's always in scope
from .env import env, env_bool, env_int, env_list


DJANGO_ENV = "development"
DEBUG = True
SECRET_KEY = env(
    "SECRET_KEY",
    "dev-insecure-key-change-before-production-!!!",
)
DB_HOST = env("DB_HOST", env("POSTGRES_HOST", "localhost"))

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "*") # noqa: F405

if module_available("debug_toolbar"): # noqa: F405
    INSTALLED_APPS += ["debug_toolbar"] # noqa: F405
    MIDDLEWARE.insert( # noqa: F405
        0,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

INTERNAL_IPS = ["127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB_NAME", "writing_system_db"),
        "USER": env("POSTGRES_USER_NAME", "postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", "postgres"),
        "HOST": DB_HOST,
        "PORT": env_int("DB_PORT", 5432),
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {
            "connect_timeout": env_int("DB_CONNECT_TIMEOUT", 10),
        },
    },
}

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", True) # noqa: F405

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

STORAGE_BACKEND = env("STORAGE_BACKEND", "local")
USE_S3 = env_bool("USE_S3", False)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media" # noqa: F405

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("ROOT_LOG_LEVEL", "DEBUG"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": env("DJANGO_DB_LOG_LEVEL", "WARNING"),
        },
        "writing_system": {
            "handlers": ["console"],
            "level": env("WRITING_SYSTEM_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
    },
}

SILENCED_SYSTEM_CHECKS = [
    *SILENCED_SYSTEM_CHECKS, # noqa: F405
    "notifications_system.W001",
]

# Use DB sessions locally — no Redis required
SESSION_ENGINE = "django.contrib.sessions.backends.db"
