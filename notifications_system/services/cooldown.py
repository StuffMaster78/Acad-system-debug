"""Simple per-user per-event throttle helper."""

from __future__ import annotations

from datetime import timedelta
from django.utils import timezone

from notifications_system.models.notifications import Notification


def should_throttle_user(
    user,
    event: str,
    cooldown_secs: int = 3600,
) -> bool:
    """Check if a user has triggered an event within cooldown.

    Args:
        user: User instance.
        event: Event key (string).
        cooldown_secs: Cooldown period in seconds (default: 3600).

    Returns:
        True if throttled (recent event exists), False otherwise.
    """
    cutoff = timezone.now() - timedelta(seconds=cooldown_secs)
    return Notification.objects.filter(
        user=user,
        event=event,
        created_at__gte=cutoff,
    ).exists()