"""Map notification priority → email template."""

from __future__ import annotations
from notifications_system.enums import NotificationPriority

TEMPLATE_MAP: dict[int, str] = {
    NotificationPriority.EMERGENCY: "notifications/emails/critical.html",
    NotificationPriority.HIGH: "notifications/emails/high.html",
    NotificationPriority.MEDIUM_HIGH: "notifications/emails/normal.html",
    NotificationPriority.NORMAL: "notifications/emails/normal.html",
    NotificationPriority.LOW: "notifications/emails/low.html",
    NotificationPriority.PASSIVE: "notifications/emails/passive.html",
}

DEFAULT_TEMPLATE = "notifications/emails/normal.html"


def get_template_for_priority(priority: int) -> str:
    """Return the appropriate email template for a given priority.

    Args:
        priority: A NotificationPriority enum value.

    Returns:
        str: Template path for rendering the email.
    """
    return TEMPLATE_MAP.get(priority, DEFAULT_TEMPLATE)