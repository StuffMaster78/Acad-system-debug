from __future__ import annotations

from django.core.cache import cache

from governance.exceptions import IdempotencyConflictError


class IdempotencyService:
    """
    Prevents duplicate execution.
    """

    TTL_SECONDS = 300

    @classmethod
    def check_and_lock(
        cls,
        key: str,
    ) -> None:

        acquired = cache.add(
            key,
            "locked",
            timeout=cls.TTL_SECONDS,
        )

        if not acquired:
            raise IdempotencyConflictError(
                f"Duplicate execution detected: {key}"
            )

    @classmethod
    def release(
        cls,
        key: str,
    ) -> None:

        cache.delete(key)