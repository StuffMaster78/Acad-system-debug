"""
notifications_system/services/broadcast_services.py

Creates broadcast records and fans out delivery to recipients.
Fan-out is async — a Celery task handles per-user notify() calls
so the request returns immediately after writing the broadcast row.
"""
from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from django.db.models import QuerySet
from django.utils import timezone
from django.conf import settings

from notifications_system.enums import (
    NotificationChannel,
    NotificationPriority,
)

logger = logging.getLogger(__name__)


class BroadcastService:
    """
    High-level API for system-wide and website-wide broadcast notifications.

    Broadcasts are admin-triggered notifications sent to multiple users.
    Fan-out is always async — the broadcast row is written synchronously,
    per-user delivery is queued to Celery.
    """

    @staticmethod
    def send_broadcast(
        *,
        event_key: str,
        title: str,
        message: str,
        website=None,
        channels: Optional[Iterable[str]] = None,
        target_roles: Optional[List[str]] = None,
        show_to_all: bool = False,
        is_blocking: bool = False, 
        triggered_by=None,
        priority: str = NotificationPriority.NORMAL,
        is_critical: bool = False,
        require_acknowledgement: bool = False,
        scheduled_for=None,
        expires_at=None,
    ):
        """
        Create a broadcast and queue async fan-out to recipients.

        Args:
            event_key:              Event key e.g. 'system.broadcast'
            title:                  Broadcast title
            message:                Broadcast body text
            website:                Website to scope to — None means platform-wide
            channels:               Override channels — None uses event config defaults
            target_roles:           Roles to target e.g. ['writer', 'client']
            show_to_all:            If True ignores target_roles and sends to everyone
            triggered_by:           Staff member creating the broadcast
            priority:               NotificationPriority value
            is_critical:            If True bypasses user mute and DND
            require_acknowledgement: If True users must acknowledge the broadcast
            scheduled_for:          Optional future send time
            expires_at:             Optional expiry datetime

        Returns:
            BroadcastNotification instance
        """
        from notifications_system.models.broadcast_notification import (
            BroadcastNotification,
        )

        broadcast = BroadcastNotification.objects.create(
            event_type=event_key,
            title=title,
            message=message,
            website=website,
            channels=list(channels) if channels else [
                NotificationChannel.IN_APP,
                NotificationChannel.EMAIL,
            ],
            target_roles=target_roles or [],
            show_to_all=show_to_all,
            created_by=triggered_by,
            is_blocking=is_blocking,
            require_acknowledgement=require_acknowledgement,
            scheduled_for=scheduled_for,
            expires_at=expires_at,
            is_active=True,
        )

        # Queue async fan-out — never block the request
        if not scheduled_for or scheduled_for <= timezone.now():
            BroadcastService._queue_fanout(broadcast.pk)
        else:
            logger.info(
                "send_broadcast() scheduled: broadcast=%s for=%s.",
                broadcast.pk,
                scheduled_for,
            )

        return broadcast

    @staticmethod
    def _queue_fanout(broadcast_id: int) -> None:
        """Queue the Celery task that fans out per-user notify() calls."""
        try:
            from notifications_system.tasks.send import process_broadcast_fanout
            process_broadcast_fanout.delay(broadcast_id) # type: ignore[attr-defined]
        except Exception as exc:
            logger.error(
                "_queue_fanout() failed to queue task: broadcast=%s error=%s.",
                broadcast_id,
                exc,
            )

    @staticmethod
    def fanout(broadcast_id: int) -> None:
        """
        Execute fan-out for a broadcast.
        Called by process_broadcast_fanout Celery task.
        Resolves recipients and calls NotificationService.notify() per user.
        """
        from notifications_system.models.broadcast_notification import (
            BroadcastNotification,
        )
        from notifications_system.services.notification_service import (
            NotificationService,
        )

        try:
            broadcast = BroadcastNotification.objects.get(id=broadcast_id)
        except BroadcastNotification.DoesNotExist:
            logger.warning(
                "fanout() broadcast not found: id=%s.", broadcast_id
            )
            return

        if broadcast.is_expired:
            logger.info(
                "fanout() skipped: broadcast=%s is expired.", broadcast_id
            )
            return

        recipients = BroadcastService._resolve_recipients(broadcast)
        context = {
            'title': broadcast.title,
            'message': broadcast.message,
            'broadcast_id': broadcast.pk,
            'website_name': broadcast.website.name if broadcast.website else '',
        }

        queued = 0
        for recipient in recipients.iterator():
            if not broadcast.is_visible_to(recipient):
                continue

            NotificationService.notify(
                event_key=broadcast.event_type,
                recipient=recipient,
                website=broadcast.website,
                context=context,
                channels=broadcast.channels or None,
                triggered_by=broadcast.created_by,
                is_critical=False,
                is_broadcast=True,
            )
            queued += 1

        # Mark broadcast as sent
        broadcast.sent_at = timezone.now()
        broadcast.save(update_fields=['sent_at'])

        logger.info(
            "fanout() complete: broadcast=%s recipients=%s.",
            broadcast_id,
            queued,
        )

    @staticmethod
    def _resolve_recipients(broadcast) -> QuerySet:
        """
        Resolve recipient queryset for a broadcast.
        Website-scoped unless show_to_all with no website = platform-wide.
        """
        User = settings.AUTH_USER_MODEL

        qs = User.objects.filter(is_active=True)

        if broadcast.website:
            qs = qs.filter(website=broadcast.website)

        if not broadcast.show_to_all and broadcast.target_roles:
            qs = qs.filter(role__in=broadcast.target_roles)

        return qs

    @staticmethod
    def preview_to_user(
        *,
        event_key: str,
        title: str,
        message: str,
        user,
        website=None,
        channels: Optional[Iterable[str]] = None,
        triggered_by=None,
    ) -> None:
        """
        Send a broadcast preview to a single user for review.
        Does not create a BroadcastNotification row.
        """
        from notifications_system.services.notification_service import (
            NotificationService,
        )

        NotificationService.notify(
            event_key=event_key,
            recipient=user,
            website=website,
            context={
                'title': title,
                'message': message,
                'is_preview': True,
            },
            channels=list(channels) if channels else None,
            triggered_by=triggered_by,
        )

    @staticmethod
    def cancel_broadcast(broadcast_id: int, cancelled_by=None) -> bool:
        """
        Cancel a scheduled broadcast before it fires.
        Returns True if cancelled, False if already sent or not found.
        """
        from notifications_system.models.broadcast_notification import (
            BroadcastNotification,
        )

        try:
            broadcast = BroadcastNotification.objects.get(id=broadcast_id)
        except BroadcastNotification.DoesNotExist:
            return False

        if broadcast.sent_at:
            logger.warning(
                "cancel_broadcast() already sent: broadcast=%s.", broadcast_id
            )
            return False

        broadcast.is_active = False
        broadcast.archived_at = timezone.now()
        broadcast.save(update_fields=['is_active', 'archived_at'])

        logger.info(
            "cancel_broadcast() cancelled: broadcast=%s by=%s.",
            broadcast_id,
            getattr(cancelled_by, 'id', None),
        )
        return True