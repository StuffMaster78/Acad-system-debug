from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # CORE
    DEBUG: bool = False
    SECRET_KEY: str
    DJANGO_ENV: str = "development"

    ALLOWED_HOSTS: list[str] = ["localhost"]
    FRONTEND_URL: str = "http://localhost:5173"

    # DATABASE
    POSTGRES_DB_NAME: str | None = None
    POSTGRES_USER_NAME: str | None = None
    POSTGRES_PASSWORD: str | None = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    # CELERY
    CELERY_TASK_TIME_LIMIT: int = 1800

    # EMAIL
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str | None = None
    EMAIL_HOST_PASSWORD: str | None = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()