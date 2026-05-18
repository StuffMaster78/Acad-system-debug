import os
from .core import get_settings

settings = get_settings()


def get_environment():
    return os.getenv("DJANGO_ENV") or (
        "development" if settings.DEBUG else "production"
    )


ENV = get_environment()