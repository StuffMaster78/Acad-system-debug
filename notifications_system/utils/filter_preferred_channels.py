"""Filter channels by user preferences."""

from __future__ import annotations

from typing import Iterable, List

from notifications_system.enums import NotificationType


def filter_channels_by_user_preferences(
    *, user, channels: Iterable[str], website=None
) -> List[str]:
    """Filter candidate channels using the user's preferences.

    Args:
        user: Authenticated user with preferences relation.
        channels: Candidate channels to consider.
        website: Optional tenant/site for scoping preferences.

    Returns:
        list[str]: Channels allowed by the user's preferences.

    Notes:
        If preferences are missing, returns the input list unchanged.
    """
    prefs = getattr(user, "notification_preferences", None)
    if not prefs:
        return list(channels)

    allowed: list[str] = []
    for ch in channels:
        if ch == NotificationType.EMAIL and getattr(prefs, "receive_email", True):
            allowed.append(ch)
        elif ch == NotificationType.SMS and getattr(prefs, "receive_sms", True):
            allowed.append(ch)
        elif ch == NotificationType.PUSH and getattr(prefs, "receive_push", True):
            allowed.append(ch)
        elif ch == NotificationType.IN_APP and getattr(prefs, "receive_in_app", True):
            allowed.append(ch)
        elif ch == NotificationType.WEBHOOK and getattr(prefs, "receive_webhook", True):
            allowed.append(ch)
        elif ch == NotificationType.SSE and getattr(prefs, "receive_sse", True):
            allowed.append(ch)
        elif ch == NotificationType.WS and getattr(prefs, "receive_ws", True):
            allowed.append(ch)
        # Unknown channels fall through and are excluded by default.
    return allowed