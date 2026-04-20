"""
Quote input validators for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError


def require_positive_int(
    payload: dict,
    key: str,
    label: str,
) -> int:
    """
    Validate that a payload value is a positive integer.
    """
    value = payload.get(key)
    if value is None:
        raise ValidationError({key: f"{label} is required."})
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(
            {key: f"{label} must be a positive integer."}
        )
    return value


def require_string(
    payload: dict,
    key: str,
    label: str,
) -> str:
    """
    Validate that a payload value is a non-empty string.
    """
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({key: f"{label} is required."})
    return value.strip()


def optional_string(
    payload: dict,
    key: str,
) -> str:
    """
    Return an optional stripped string value.
    """
    value = payload.get(key)
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError({key: "Value must be a string."})
    return value.strip()


def optional_positive_int(
    payload: dict,
    key: str,
) -> int | None:
    """
    Return an optional positive integer value.
    """
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(
            {key: "Value must be a positive integer."}
        )
    return value