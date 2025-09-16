"""Cached access to user notification preferences."""

from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.core.cache import cache

from notifications_system.models.notification_preferences import (
    NotificationPreference,
)
from notifications_system.services.preferences import (
    NotificationPreferenceResolver,
)


DEFAULT_TTL = getattr(settings, "NOTIF_PREF_CACHE_TTL", 3600)


def _cache_key(user_id: int, website_id: Optional[int]) -> str:
    """Build a stable cache key scoped by user and website."""
    wid = website_id if website_id is not None else "none"
    return f"notif_prefs:{user_id}:{wid}"


def get_cached_preferences(user) -> Optional[NotificationPreference]:
    """Return preferences from cache/DB, creating defaults if missing.

    Args:
        user: Authenticated user instance with optional `.website`.

    Returns:
        NotificationPreference or None if user is invalid/anonymous.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return None

    website = getattr(user, "website", None)
    key = _cache_key(getattr(user, "id", 0), getattr(website, "id", None))

    pref: Optional[NotificationPreference] = cache.get(key)
    if pref:
        return pref

    try:
        pref = NotificationPreference.objects.get(user=user, website=website)
    except NotificationPreference.DoesNotExist:
        pref = NotificationPreferenceResolver.assign_default_preferences(
            user=user, website=website
        )

    cache.set(key, pref, timeout=DEFAULT_TTL)
    return pref


def invalidate_preferences_cache(user_id: int, website_id: Optional[int]) -> None:
    """Remove a single user+website preference entry from cache."""
    cache.delete(_cache_key(user_id, website_id))


def update_preferences_cache(user) -> None:
    """Refresh the cache entry for the given user (current website).

    Args:
        user: User instance whose preferences should be re-cached.
    """
    website = getattr(user, "website", None)
    try:
        pref = NotificationPreference.objects.get(user=user, website=website)
    except NotificationPreference.DoesNotExist:
        pref = NotificationPreferenceResolver.assign_default_preferences(
            user=user, website=website
        )

    cache.set(
        _cache_key(getattr(user, "id", 0), getattr(website, "id", None)),
        pref,
        timeout=DEFAULT_TTL,
    )