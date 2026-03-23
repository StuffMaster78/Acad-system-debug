# notifications_system/services/inapp_service.py
"""
In-app notification service.

Provides a clean query and mutation layer for the in-app
notification feed, read state, pin state, and unread count.

Views delegate to this service instead of querying models
directly. This keeps the views thin and the business logic
in one place.

Note on delivery:
    Delivery of in-app notifications (incrementing unread count,
    updating last_notified_at) is handled by InAppBackend.
    This service owns everything that happens after delivery —
    reading, marking, pinning, acknowledging, and querying.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.db.models import QuerySet
from django.utils import timezone

from notifications_system.enums import (
    DeliveryStatus,
    NotificationPriority,
)

logger = logging.getLogger(__name__)


class InAppService:
    """
    Query and mutation layer for the in-app notification feed.

    Responsibilities:
        - Feed queries (all, unread, pinned, filtered)
        - Mark read / mark all read
        - Pin / unpin
        - Acknowledge
        - Unread count reads and resets
        - Touch last_seen_at (user opened the notification panel)
    """

    # ─────────────────────────────────────────────────────────
    # Feed queries
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def get_feed(
        user,
        website,
        *,
        exclude_cancelled: bool = True,
        exclude_expired: bool = True,
    ) -> QuerySet:
        """
        Return the base notification feed queryset for a user.

        Always scoped to user + website.
        Ordered newest first.
        Excludes cancelled and expired by default.

        Args:
            user:               Recipient user
            website:            Website for tenant scoping
            exclude_cancelled:  Exclude CANCELLED status rows
            exclude_expired:    Exclude rows past their expires_at

        Returns:
            Notification QuerySet — not yet evaluated.
        """
        from notifications_system.models.notifications import Notification

        qs = Notification.objects.filter(
            user=user,
            website=website,
        ).select_related('website').order_by('-created_at')

        if exclude_cancelled:
            qs = qs.exclude(status=DeliveryStatus.CANCELLED)

        if exclude_expired:
            qs = qs.exclude(
                expires_at__isnull=False,
                expires_at__lt=timezone.now(),
            )

        return qs

    @staticmethod
    def get_unread(user, website) -> QuerySet:
        """
        Return unread notifications for a user.
        Excludes pinned — pinned have their own section.
        """
        from notifications_system.models.notifications import Notification
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        unread_ids = NotificationsUserStatus.objects.filter(
            user=user,
            website=website,
            is_read=False,
            is_pinned=False,
        ).values_list('notification_id', flat=True)

        return Notification.objects.filter(
            id__in=unread_ids,
            website=website,
        ).exclude(
            status=DeliveryStatus.CANCELLED,
        ).order_by('-created_at')

    @staticmethod
    def get_pinned(user, website) -> QuerySet:
        """
        Return all pinned notifications for a user.
        Ordered by when they were pinned, newest first.
        """
        from notifications_system.models.notifications import Notification
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        pinned_ids = NotificationsUserStatus.objects.filter(
            user=user,
            website=website,
            is_pinned=True,
        ).order_by('-pinned_at').values_list('notification_id', flat=True)

        # Preserve pinned order
        from django.db.models import Case, When
        preserved_order = Case(
            *[When(id=pk, then=pos) for pos, pk in enumerate(pinned_ids)]
        )
        return Notification.objects.filter(
            id__in=pinned_ids,
        ).order_by(preserved_order)

    @staticmethod
    def get_by_category(user, website, category: str) -> QuerySet:
        """Return notifications filtered by category."""
        return InAppService.get_feed(user, website).filter(
            category=category,
        )

    @staticmethod
    def get_critical(user, website) -> QuerySet:
        """Return unread critical notifications."""
        return InAppService.get_feed(user, website).filter(
            is_critical=True,
            notificationsuserstatus__is_read=False,
            notificationsuserstatus__user=user,
        )

    @staticmethod
    def get_for_poll(user, website) -> Optional[Dict[str, Any]]:
        """
        Return the minimal payload needed for the poll endpoint.

        Returns the most recent unread notification for toast display
        alongside the cached unread count. Designed to be fast —
        one integer read and one indexed query.

        Returns:
            Dict with 'unread_count' and 'latest' or None.
        """
        from notifications_system.models.notifications import Notification
        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        meta, _ = UserNotificationMeta.objects.get_or_create(
            user=user,
            website=website,
        )

        # Most recent unread notification for toast
        unread_notification_ids = NotificationsUserStatus.objects.filter(
            user=user,
            website=website,
            is_read=False,
        ).values_list('notification_id', flat=True)

        latest = Notification.objects.filter(
            id__in=unread_notification_ids,
            status=DeliveryStatus.SENT,
        ).order_by('-created_at').first()

        return {
            'unread_count': meta.unread_count,
            'latest': {
                'id': latest.id,
                'title': latest.title,
                'message': latest.message,
                'event_key': latest.event_key,
                'category': latest.category,
                'created_at': latest.created_at.isoformat(),
            } if latest else None,
        }

    # ─────────────────────────────────────────────────────────
    # Read state mutations
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def mark_read(
        user,
        website,
        notification_id: int,
    ) -> bool:
        """
        Mark a single notification as read.

        Updates the NotificationsUserStatus row and recalculates
        the cached unread count from source of truth.

        Args:
            user:            Recipient user
            website:         Website for tenant scoping
            notification_id: Notification PK to mark read

        Returns:
            True if found and marked.
            False if not found or wrong user/website.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        try:
            user_status = NotificationsUserStatus.objects.get(
                notification_id=notification_id,
                user=user,
                website=website,
            )
        except NotificationsUserStatus.DoesNotExist:
            logger.warning(
                "InAppService.mark_read(): status not found "
                "for notification=%s user=%s website=%s.",
                notification_id,
                user.id,
                website.id,
            )
            return False

        if user_status.is_read:
            # Already read — no-op but return True
            return True

        user_status.mark_read()
        InAppService._recalculate_unread(user, website)

        logger.debug(
            "InAppService.mark_read(): notification=%s user=%s.",
            notification_id,
            user.id,
        )
        return True

    @staticmethod
    def mark_all_read(user, website) -> int:
        """
        Mark all unread notifications as read for a user.

        Bulk updates NotificationsUserStatus rows and resets
        the cached unread count to zero.

        Returns:
            Count of rows marked read.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )
        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )

        now = timezone.now()
        updated = NotificationsUserStatus.objects.filter(
            user=user,
            website=website,
            is_read=False,
        ).update(is_read=True, read_at=now)

        # Reset cached count to zero — all read
        UserNotificationMeta.objects.filter(
            user=user,
            website=website,
        ).update(unread_count=0)

        logger.info(
            "InAppService.mark_all_read(): marked %s read "
            "for user=%s website=%s.",
            updated,
            user.id,
            website.id,
        )
        return updated

    # ─────────────────────────────────────────────────────────
    # Pin state mutations
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def pin(user, website, notification_id: int) -> bool:
        """
        Pin a notification.

        Returns:
            True if found and pinned.
            False if not found.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        try:
            user_status = NotificationsUserStatus.objects.get(
                notification_id=notification_id,
                user=user,
                website=website,
            )
        except NotificationsUserStatus.DoesNotExist:
            return False

        user_status.pin()
        return True

    @staticmethod
    def unpin(user, website, notification_id: int) -> bool:
        """
        Unpin a notification.

        Returns:
            True if found and unpinned.
            False if not found.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        try:
            user_status = NotificationsUserStatus.objects.get(
                notification_id=notification_id,
                user=user,
                website=website,
            )
        except NotificationsUserStatus.DoesNotExist:
            return False

        user_status.unpin()
        return True

    # ─────────────────────────────────────────────────────────
    # Acknowledge
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def acknowledge(user, website, notification_id: int) -> bool:
        """
        Acknowledge a notification.
        Used for critical or action-required notifications.

        Returns:
            True if found and acknowledged.
            False if not found.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        try:
            user_status = NotificationsUserStatus.objects.get(
                notification_id=notification_id,
                user=user,
                website=website,
            )
        except NotificationsUserStatus.DoesNotExist:
            return False

        user_status.acknowledge()
        return True

    # ─────────────────────────────────────────────────────────
    # Unread count
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def get_unread_count(user, website) -> int:
        """
        Return the cached unread count for a user.
        Creates the meta row if it does not exist.

        This is the fast path — one integer read, no COUNT query.
        Used by the bell icon and poll endpoint.
        """
        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )

        meta, _ = UserNotificationMeta.objects.get_or_create(
            user=user,
            website=website,
        )
        return meta.unread_count

    @staticmethod
    def touch(user, website) -> None:
        """
        Update last_seen_at for a user.
        Called when the user opens the notification panel.
        Used to calculate unseen notifications since last visit.
        """
        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )

        UserNotificationMeta.objects.filter(
            user=user,
            website=website,
        ).update(last_seen_at=timezone.now())

    # ─────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _recalculate_unread(user, website) -> int:
        """
        Recalculate unread count from source of truth and
        update the cached value.

        Called after mark_read() to keep the cache accurate.
        Not called after mark_all_read() — that resets to zero directly.

        Returns:
            The recalculated count.
        """
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )
        from notifications_system.models.user_notification_meta import (
            UserNotificationMeta,
        )

        count = NotificationsUserStatus.objects.filter(
            user=user,
            website=website,
            is_read=False,
        ).count()

        UserNotificationMeta.objects.filter(
            user=user,
            website=website,
        ).update(unread_count=count)

        return count