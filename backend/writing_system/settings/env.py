from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
APPS_DIR = BASE_DIR / "writing_system"

load_dotenv(BASE_DIR / ".env")


def env(
    key: str,
    default: Any = None,
    *,
    required: bool = False,
    allow_empty: bool = False,
) -> Any:
    """
    Read an environment variable with optional strict validation.
    """
    value = os.getenv(key, default)

    if required and (value is None or (value == "" and not allow_empty)):
        raise ImproperlyConfigured(f"Missing required env var: {key}")

    if value == "" and not allow_empty:
        return default

    return value


def env_bool(key: str, default: bool = False) -> bool:
    """
    Read a boolean environment variable.
    """
    value = str(env(key, str(default))).strip().lower()
    return value in {"1", "true", "yes", "on"}


def env_int(key: str, default: int) -> int:
    """
    Read an integer environment variable.
    """
    value = env(key, default)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            f"Environment variable {key} must be an integer."
        ) from exc


def env_list(
    key: str,
    default: str | list[str] = "",
    *,
    separator: str = ",",
    required: bool = False,
) -> list[str]:
    """
    Read a comma-separated environment variable.
    """
    value = env(key, default, required=required)

    if isinstance(value, list):
        return value

    return [
        item.strip()
        for item in str(value).split(separator)
        if item.strip()
    ]


def require_envs(keys: list[str]) -> None:
    """
    Ensure all listed variables are present and non-empty.
    """
    missing = [
        key
        for key in keys
        if os.getenv(key) in {None, ""}
    ]

    if missing:
        joined = ", ".join(missing)
        raise ImproperlyConfigured(
            f"Missing required environment variables: {joined}"
        )
