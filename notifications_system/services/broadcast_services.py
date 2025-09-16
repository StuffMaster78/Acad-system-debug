"""Broadcast notification service.

Creates a broadcast record, selects recipients, and fans out delivery via
NotificationService so all channels, retries, fallbacks, and logging are
consistent with the rest of the system.
"""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from notifications_system.enums import DeliveryStatus, NotificationType
from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
)
from notifications_system.models.notification_delivery import (
    NotificationDelivery,
)
from notifications_system.services.core import NotificationService

logger = logging.getLogger(__name__)
User = get_user_model()


class BroadcastNotificationService:
    """High-level API for system/website broadcast notifications."""

    @staticmethod
    def _resolve_recipients(group: Optional[str] = None) -> QuerySet:
        """Return active users, optionally filtered by a Django group name."""
        qs = User.objects.filter(is_active=True)
        if group:
            qs = qs.filter(groups__name=group)
        return qs

    @classmethod
    def send_broadcast(
        cls,
        *,
        event: str,
        title: str,
        message: str,
        website=None,
        channels: Optional[Iterable[str]] = None,
        group: Optional[str] = None,
        is_test: bool = False,
        priority: int = 5,
    ) -> BroadcastNotification:
        """Create and fan out a broadcast.

        Args:
            event: Event key to render (e.g., "broadcast.system_announcement").
            title: Broadcast title.
            message: Broadcast text/plain body.
            website: Tenant/site object.
            channels: Optional explicit channels (e.g., ["in_app", "email"]).
            group: Optional Django auth group name to target.
            is_test: If True, mark the broadcast as test.
            priority: Priority integer (mapped the same as other sends).

        Returns:
            The created BroadcastNotification row.
        """
        # Persist the broadcast object for auditing.
        broadcast = BroadcastNotification.objects.create(
            event_type=event,
            title=title,
            message=message,
            context={"is_test": is_test},
            website=website,
            priority=priority,
            is_active=True,
            is_test=is_test,
        )

        recipients = cls._resolve_recipients(group=group).iterator()
        payload = {"title": title, "message": message}

        for user in recipients:
            # Delegate to NotificationService for unified behavior.
            notif = NotificationService.send_notification(
                user=user,
                event=event,
                payload=payload,
                website=website,
                channels=list(channels) if channels else None,
                is_critical=False,
                global_broadcast=False,
            )

            # Mirror a per-recipient delivery record.
            try:
                NotificationDelivery.objects.create(
                    notification=notif,
                    user=user,
                    channel=(notif.type if notif else NotificationType.IN_APP),
                    status=(DeliveryStatus.SENT if notif
                            else DeliveryStatus.FAILED),
                    error_message=("creation failed" if not notif else None),
                    attempts=1,
                )
            except Exception:  # noqa: BLE001
                logger.debug(
                    "Delivery record write failed for user=%s broadcast=%s",
                    getattr(user, "id", None),
                    getattr(broadcast, "id", None),
                    exc_info=True,
                )

        return broadcast

    @classmethod
    def preview_to_user(
        cls,
        *,
        event: str,
        title: str,
        message: str,
        user,
        website=None,
        channels: Optional[Iterable[str]] = None,
        priority: int = 5,
    ) -> None:
        """Send a preview of a broadcast to a single user.

        Args:
            event: Event key.
            title: Preview title.
            message: Preview body.
            user: Target user.
            website: Tenant/site object.
            channels: Optional explicit channels.
            priority: Priority integer.
        """
        payload = {"title": title, "message": message, "is_preview": True}
        NotificationService.send_notification(
            user=user,
            event=event,
            payload=payload,
            website=website,
            channels=list(channels) if channels else None,
            is_critical=False,
            global_broadcast=False,
            priority=priority,
        )