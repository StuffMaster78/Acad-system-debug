"""Renderer for priority-based notification emails."""

from __future__ import annotations

from typing import Any, Dict, Optional

from django.template.loader import render_to_string

from notifications_system.enums import NotificationPriority

TEMPLATE_MAP: dict[NotificationPriority, str] = {
    NotificationPriority.EMERGENCY: "notifications/emails/critical.html",
    NotificationPriority.HIGH: "notifications/emails/high.html",
    NotificationPriority.MEDIUM_HIGH: "notifications/emails/high.html",
    NotificationPriority.NORMAL: "notifications/emails/normal.html",
    NotificationPriority.LOW: "notifications/emails/low.html",
    NotificationPriority.PASSIVE: "notifications/emails/passive.html",
}

DEFAULT_TEMPLATE: str = "notifications/emails/normal.html"


def render_notification_email(
    subject: str,
    message: str,
    *,
    context: Optional[Dict[str, Any]] = None,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    template_name: Optional[str] = None,
) -> str:
    """Render an email body for a notification.

    Args:
        subject: Email subject string.
        message: Plaintext message string.
        context: Extra context vars for the template.
        priority: Notification priority; determines which template to use.
        template_name: Explicit template override (bypasses priority map).

    Returns:
        Rendered HTML string.
    """
    ctx: dict[str, Any] = dict(context or {})
    ctx.update({"subject": subject, "message": message})

    template = template_name or TEMPLATE_MAP.get(priority, DEFAULT_TEMPLATE)
    return render_to_string(template, ctx)