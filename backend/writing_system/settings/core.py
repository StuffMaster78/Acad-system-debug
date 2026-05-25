from __future__ import annotations

from functools import lru_cache

from .env import env, env_bool, env_int, env_list


class Settings:
    """
    Lightweight compatibility wrapper for older code that imports
    writing_system.settings.core.get_settings().
    """

    DEBUG = env_bool("DEBUG", False)
    SECRET_KEY = env("SECRET_KEY", "dev-insecure-secret-key-change-me")
    DJANGO_ENV = env("DJANGO_ENV", "development")
    ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost")
    FRONTEND_URL = env("FRONTEND_URL", "http://localhost:5173")
    POSTGRES_DB_NAME = env("POSTGRES_DB_NAME", "writing_system_db")
    POSTGRES_USER_NAME = env("POSTGRES_USER_NAME", "postgres")
    POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", "")
    DB_HOST = env("DB_HOST", env("POSTGRES_HOST", "localhost"))
    DB_PORT = env_int("DB_PORT", 5432)
    REDIS_HOST = env("REDIS_HOST", "localhost")
    REDIS_PORT = env_int("REDIS_PORT", 6379)
    REDIS_PASSWORD = env("REDIS_PASSWORD", "")
    CELERY_TASK_TIME_LIMIT = env_int("CELERY_TASK_TIME_LIMIT", 1800)
    EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = env_int("EMAIL_PORT", 587)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")


@lru_cache
def get_settings():
    return Settings()
