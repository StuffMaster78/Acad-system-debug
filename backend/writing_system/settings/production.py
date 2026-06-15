from __future__ import annotations

"""
Production settings. All secrets must come from environment variables.
"""

import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import * # noqa: F401,F403
from .env import env, env_bool, env_int, env_list, require_envs


DJANGO_ENV = "production"
DEBUG = False

require_envs(
    [
        "SECRET_KEY",
        "ALLOWED_HOSTS",
        "POSTGRES_DB_NAME",
        "POSTGRES_USER_NAME",
        "POSTGRES_PASSWORD",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "DEFAULT_EMAIL_PROVIDER",
        "FIELD_ENCRYPTION_KEY",
        "TOKEN_ENCRYPTION_KEY",
        "CORS_ALLOWED_ORIGINS",
        "CSRF_TRUSTED_ORIGINS",
    ]
)

if SECRET_KEY == "dev-insecure-secret-key-change-me": # noqa: F405
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("SECRET_KEY must be set in production.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", required=True)
DB_HOST = env("DB_HOST", env("POSTGRES_HOST", "db"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB_NAME", required=True),
        "USER": env("POSTGRES_USER_NAME", required=True),
        "PASSWORD": env("POSTGRES_PASSWORD", required=True),
        "HOST": DB_HOST,
        "PORT": env_int("DB_PORT", 5432),
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 600),
        "ATOMIC_REQUESTS": env_bool("DB_ATOMIC_REQUESTS", False),
        "OPTIONS": {
            "connect_timeout": env_int("DB_CONNECT_TIMEOUT", 10),
        },
    },
}

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    True,
)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")
CORS_ALLOW_ALL_ORIGINS = False

SENDGRID_API_KEY = env("SENDGRID_API_KEY", "")
if module_available("anymail") and SENDGRID_API_KEY: # noqa: F405
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {
        "SENDGRID_API_KEY": SENDGRID_API_KEY,
    }
else:
    EMAIL_BACKEND = env(
        "EMAIL_BACKEND",
        "django.core.mail.backends.smtp.EmailBackend",
    )

STORAGE_BACKEND = env("STORAGE_BACKEND", "s3")
USE_S3 = env_bool("USE_S3", True)

if USE_S3:
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", required=True)
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", required=True)
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", required=True)
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
        "ServerSideEncryption": "AES256",
    }

    if STORAGE_BACKEND == "do_spaces":
        DO_SPACES_REGION = env("DO_SPACES_REGION", "nyc3")
        AWS_S3_ENDPOINT_URL = (
            f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"
        )
        AWS_S3_REGION_NAME = DO_SPACES_REGION
        AWS_S3_CUSTOM_DOMAIN = env("DO_SPACES_CDN_ENDPOINT", "")
    else:
        AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", "us-east-1")
        AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", "")

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    elif STORAGE_BACKEND == "do_spaces":
        MEDIA_URL = (
            f"https://{AWS_STORAGE_BUCKET_NAME}."
            f"{AWS_S3_REGION_NAME}.digitaloceanspaces.com/media/"
        )
    else:
        MEDIA_URL = (
            f"https://{AWS_STORAGE_BUCKET_NAME}.s3."
            f"{AWS_S3_REGION_NAME}.amazonaws.com/media/"
        )

    STORAGES = {
        **STORAGES, # noqa: F405
        "default": {
            "BACKEND": "core.storage_backends.MediaStorage",
        },
    }

LOG_DIR = env("LOG_DIR", "/var/log/writing-system")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "{levelname} {asctime} {module} "
                "{process:d} {thread:d} {message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/security.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": env("ROOT_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file"],
            "level": env("DJANGO_SECURITY_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "writing_system": {
            "handlers": ["file", "console"],
            "level": env("WRITING_SYSTEM_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "celery": {
            "handlers": ["file", "console"],
            "level": env("CELERY_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["file", "console"],
            "level": env("CELERY_TASK_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "celery.utils.functional": {
            "handlers": ["file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "audit": {
            "handlers": ["file", "console"],
            "level": env("AUDIT_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
    },
}

SENTRY_DSN = env("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(env("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        environment=env("SENTRY_ENVIRONMENT", "production"),
        release=env("APP_VERSION", "unknown"),
    )

# ── API schema & docs: restrict to admin users in production ─────────────────
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,  # noqa: F405
    "SERVE_PERMISSIONS": ["authentication.permissions.IsAdminOrSuperAdmin"],
}
