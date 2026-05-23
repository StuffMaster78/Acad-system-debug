from __future__ import annotations

import os


def get_environment() -> str:
    """
    Return the normalized runtime environment name.
    """
    return os.getenv("DJANGO_ENV", "development").strip().lower()


ENV = get_environment()
