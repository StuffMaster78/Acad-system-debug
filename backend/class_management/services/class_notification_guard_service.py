from __future__ import annotations

from django.core.cache import cache


class ClassNotificationGuardService:
    """
    Prevent noisy duplicate class notifications.
    """
    @staticmethod
    def should_send(
        *,
        event_key: str,
        class_order_id: int,
        recipient_id: int,
        ttl_seconds: int = 900,
    ) -> bool:
        cache_key = (
            f"class_notification:{event_key}:"
            f"{class_order_id}:{recipient_id}"
        )

        if cache.get(cache_key):
            return False

        cache.set(
            cache_key,
            "1",
            timeout=60,
        )
        return True