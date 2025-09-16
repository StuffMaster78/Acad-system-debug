"""Cache helpers for notification preferences."""

from __future__ import annotations

from django.core.cache import cache
from typing import Any, Optional


def cache_notification_prefs(user_id: int, prefs: Any, timeout: int = 3600) -> None:
    """Cache notification preferences for a user.

    Args:
        user_id: ID of the user.
        prefs: Preferences object or dict to store.
        timeout: Expiration in seconds (default: 1 hour).
    """
    key = f"notif_prefs:{user_id}"
    cache.set(key, prefs, timeout=timeout)


def get_cached_notification_prefs(user_id: int) -> Optional[Any]:
    """Retrieve cached notification preferences for a user.

    Args:
        user_id: ID of the user.

    Returns:
        Cached preferences or None if not found.
    """
    return cache.get(f"notif_prefs:{user_id}")


def clear_notification_prefs_cache(user_id: int) -> None:
    """Clear cached notification preferences for a user.

    Args:
        user_id: ID of the user.
    """
    cache.delete(f"notif_prefs:{user_id}")