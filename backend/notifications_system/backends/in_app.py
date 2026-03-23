# notifications_system/backends/in_app.py
from __future__ import annotations

import logging

from django.utils import timezone

from notifications_system.backends.base import (
    BaseDeliveryBackend, DeliveryResult
)

logger = logging.getLogger(__name__)


class InAppBackend(BaseDeliveryBackend):
    """
    In-app notification delivery.

    The Notification row is already persisted by the Dispatcher.
    This backend increments the user's unread count so the frontend
    bell icon reflects the new notification on next poll.
    """

    channel = 'in_app'

    def send(self) -> DeliveryResult:
        try:
            from notifications_system.models.user_notification_meta import (
                UserNotificationMeta,
            )
            meta, _ = UserNotificationMeta.objects.get_or_create(
                user=self.user,
                website=self.website,
            )
            meta.increment_unread()
            meta.last_notified_at = timezone.now()
            meta.save(update_fields=['last_notified_at', 'updated_at'])

        except Exception as exc:
            logger.exception(
                "InAppBackend: failed to update unread meta "
                "for user=%s website=%s: %s.",
                getattr(self.user, 'id', None),
                getattr(self.website, 'id', None),
                exc,
            )
            return DeliveryResult(
                success=False,
                message=f"Unread count update failed: {exc}",
                error_code='META_UPDATE_FAILED',
            )

        return DeliveryResult(
            success=True,
            message='In-app notification available.',
        )