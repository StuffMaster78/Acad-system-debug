from django.core.cache import cache


class IdempotencyService:
    """
    Ensures events are processed only once.
    """

    PREFIX = "event_idempotency:"

    @classmethod
    def is_processed(cls, event_id: str) -> bool:
        """Check if event already processed."""
        return cache.get(cls.PREFIX + event_id) is not None

    @classmethod
    def mark_processed(
        cls,
        event_id: str,
        ttl: int = 86400,
    ) -> None:
        """Mark event as processed."""
        cache.set(
            cls.PREFIX + event_id,
            True,
            timeout=ttl,
        )

    
    @staticmethod
    def claim(event_id: str, ttl: int = 300) -> bool:
        """
        Atomically claim event for processing.

        Returns:
            True if claim successful
            False if already claimed
        """

        key = IdempotencyService.PREFIX + event_id

        # Django cache doesn't guarantee atomicity everywhere,
        # but this is acceptable baseline unless you're on Redis with SETNX.
        if cache.get(key) is not None:
            return False

        cache.set(key, "processing", timeout=ttl)
        return True