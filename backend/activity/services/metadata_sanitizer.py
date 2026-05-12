from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID


class ActivityMetadataSanitizer:
    """
    Sanitizes activity metadata before storage.

    Activity metadata may be exposed in user facing feeds. Sensitive
    credentials, tokens, and secrets must never be stored here.
    """

    BLOCKED_KEYS = {
        "access_key",
        "api_key",
        "authorization",
        "credential",
        "credentials",
        "cvv",
        "password",
        "private_key",
        "refresh_token",
        "secret",
        "token",
        "otp",
        "2fa",
    }

    @classmethod
    def sanitize(
        cls,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Return sanitized metadata.

        Args:
            metadata: Raw metadata supplied by a domain service.

        Returns:
            Metadata safe enough for activity storage.
        """
        if not metadata:
            return {}

        safe_metadata: dict[str, Any] = {}

        for key, value in metadata.items():
            normalized_key = key.lower().strip()

            if normalized_key in cls.BLOCKED_KEYS:
                continue

            safe_metadata[key] = cls._sanitize_value(value)

        return safe_metadata

    @classmethod
    def _sanitize_value(cls, value: Any) -> Any:
        """
        Sanitize a metadata value recursively.
        """
        if isinstance(value, dict):
            return cls.sanitize(value)

        if isinstance(value, list):
            return [
                cls._sanitize_value(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                cls._sanitize_value(item)
                for item in value
            ]

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, UUID):
            return str(value)

        if hasattr(value, "isoformat"):
            return value.isoformat()

        if cls._is_primitive(value):
            return value

        return str(value)

    @staticmethod
    def _is_primitive(value: Any) -> bool:
        """
        Return whether a value is JSON safe without conversion.
        """
        return value is None or isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        )