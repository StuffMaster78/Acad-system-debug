from __future__ import annotations

from typing import Optional

from django.conf import settings

from notifications_system.services.core import NotificationService
from notifications_system.enums import NotificationType


def send_reset_confirmation(
    *,
    user,
    website,
    use_async: bool = True,
    force_email_to: Optional[str] = None,
) -> None:
    """Send the preferences reset confirmation via the service.

    Args:
        user: Target user.
        website: Tenant/site object.
        use_async: If True and Celery enabled, run via task.
        force_email_to: Optional override recipient email.
    """
    if use_async and getattr(settings, "USE_CELERY", False):
        from notifications_system.tasks import send_reset_email_task
        send_reset_email_task.delay(user.id, getattr(website, "id", None),
                                    force_email_to)
        return

    _send_reset_confirmation_now(
        user=user,
        website=website,
        force_email_to=force_email_to,
    )


def _send_reset_confirmation_now(
    *,
    user,
    website,
    force_email_to: Optional[str] = None,
) -> None:
    """Synchronous path using NotificationService."""
    payload = {
        "user": user,
        "website": website,
        "title": "Your notification preferences were reset",
        "message": (
            "Your notification preferences have been reset to defaults."
        ),
    }
    NotificationService.send_notification(
        user=user,
        event="preferences.reset",
        payload=payload,
        website=website,
        channels=[NotificationType.EMAIL],
        email_override=force_email_to,
        category="account",
        priority="normal",
    )