from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from django.contrib.auth import get_user_model

from notifications_system.emails.reset_notification_preferences import (
    _send_reset_confirmation_now,
)
from notifications_system.models.notifications import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, acks_late=True, ignore_result=True)
def send_reset_email_task(
    self,
    user_id: int,
    website_id: Optional[int] = None,
    force_email_to: Optional[str] = None,
) -> None:
    """Send the preferences reset email via the service (async).

    Args:
        user_id: Target user ID.
        website_id: Optional tenant/site ID.
        force_email_to: Optional override recipient email.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning("send_reset_email_task: user %s missing", user_id)
        return

    website = None
    if website_id is not None:
        # Replace with your actual Website model import.
        from notifications_system.models.notification_settings import (
            NotificationSettings,
        )
        try:
            website = NotificationSettings.objects.get(id=website_id)
        except NotificationSettings.DoesNotExist:
            logger.warning("send_reset_email_task: website %s missing",
                           website_id)

    _send_reset_confirmation_now(
        user=user,
        website=website,
        force_email_to=force_email_to,
    )