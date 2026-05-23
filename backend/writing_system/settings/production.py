from __future__ import annotations

from .base import *  # noqa: F401,F403
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
        "DB_HOST",
        "DEFAULT_EMAIL_PROVIDER",
        "FIELD_ENCRYPTION_KEY",
        "TOKEN_ENCRYPTION_KEY",
    ]
)

if SECRET_KEY == "dev-insecure-secret-key-change-me":  # noqa: F405
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured("SECRET_KEY must be set in production.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", required=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB_NAME", required=True),
        "USER": env("POSTGRES_USER_NAME", required=True),
        "PASSWORD": env("POSTGRES_PASSWORD", required=True),
        "HOST": env("DB_HOST", required=True),
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
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    True,
)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")
CORS_ALLOW_ALL_ORIGINS = False

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

STORAGE_BACKEND = env("STORAGE_BACKEND", "s3")

if STORAGE_BACKEND in {"s3", "do_spaces"}:
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

SENTRY_DSN = env("SENTRY_DSN", "")
