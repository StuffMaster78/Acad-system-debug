"""In-app notification helpers.

Utilities to create and manage in-app notifications and per-user status
rows (read/pinned/expiry). These helpers assume preference filtering
happens earlier in the pipeline (e.g., in NotificationService).
"""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from django.db import transaction
from django.db.models import Case, IntegerField, When
from django.utils import timezone

from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import (
    NotificationsUserStatus,
)

logger = logging.getLogger(__name__)


def send_in_app_notification(
    user,
    title: str,
    message: str,
    *,
    website=None,
    event_key: Optional[str] = None,
    role: Optional[str] = None,
    data: Optional[dict] = None,
    expires_at=None,
    priority: str = "normal",
    metadata: Optional[dict] = None,
) -> Optional[Notification]:
    """Create an in-app notification for a single user.

    Args:
        user: Target user.
        title: Notification title.
        message: Notification message (plain text).
        website: Optional tenant/site object.
        event_key: Optional event identifier.
        role: Optional role tag.
        data: Extra payload to persist with the notification.
        expires_at: Optional expiry datetime for the notification.
        priority: One of: low|normal|high|critical.
        metadata: Optional arbitrary metadata dict.

    Returns:
        The created Notification or None on failure.
    """
    try:
        notification = Notification.objects.create(
            title=title,
            message=message,
            type="in_app",
            website=website,
            event=event_key,  # keep consistent with your Notification model
            role=role,
            payload=data or {},
            metadata=metadata or {},
            priority=priority,
            expires_at=expires_at,
            delivery_channels=["in_app"],
        )
        _create_user_notification_status(notification, [user])
        logger.info(
            "In-app notification %s created for user %s (event=%s)",
            notification.id,
            getattr(user, "id", None),
            event_key,
        )
        return notification
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to create in-app notification for user %s: %s",
            getattr(user, "id", None),
            exc,
            exc_info=True,
        )
        return None


def send_bulk_in_app_notification(
    users: Iterable,
    title: str,
    message: str,
    *,
    website=None,
    event_key: Optional[str] = None,
    role: Optional[str] = None,
    data: Optional[dict] = None,
    expires_at=None,
    priority: str = "normal",
    metadata: Optional[dict] = None,
) -> Optional[Notification]:
    """Create a single in-app notification and attach it to many users.

    Args:
        users: Iterable of user instances.
        title: Notification title.
        message: Notification message.
        website: Optional tenant/site object.
        event_key: Optional event identifier.
        role: Optional role tag.
        data: Extra payload to persist with the notification.
        expires_at: Optional expiry datetime.
        priority: One of: low|normal|high|critical.
        metadata: Optional arbitrary metadata dict.

    Returns:
        The created Notification or None on failure.
    """
    users = list(users or [])
    if not users:
        logger.warning("No users provided for bulk in-app notification.")
        return None

    try:
        notification = Notification.objects.create(
            title=title,
            message=message,
            type="in_app",
            website=website,
            event=event_key,
            role=role,
            payload=data or {},
            metadata=metadata or {},
            priority=priority,
            expires_at=expires_at,
            delivery_channels=["in_app"],
        )
        _create_user_notification_status(notification, users)
        logger.info(
            "In-app notification %s sent to %d users (event=%s)",
            notification.id,
            len(users),
            event_key,
        )
        return notification
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Bulk in-app notification failed: %s", exc, exc_info=True
        )
        return None


def get_user_notifications(
    user,
    *,
    website=None,
    include_read: bool = True,
    limit: int = 50,
    offset: int = 0,
):
    """Fetch a user's in-app notifications with smart ordering.

    Order:
      1) pinned desc
      2) priority (critical > high > normal > low)
      3) created desc

    Args:
        user: Target user.
        website: Optional tenant/site filter.
        include_read: Include read notifications when True.
        limit: Max number of rows to return.
        offset: Offset for pagination.

    Returns:
        QuerySet of NotificationsUserStatus (prefetched notification).
    """
    filters = {
        "user": user,
        "notification__type": "in_app",
    }
    if website:
        filters["notification__website"] = website
    if not include_read:
        filters["read"] = False

    priority_order = Case(
        When(notification__priority="critical", then=1),
        When(notification__priority="high", then=2),
        When(notification__priority="normal", then=3),
        When(notification__priority="low", then=4),
        default=5,
        output_field=IntegerField(),
    )

    qs = (
        NotificationsUserStatus.objects.select_related("notification")
        .filter(**filters)
        .order_by("-pinned", priority_order, "-notification__created_at")
    )
    return qs[offset : offset + limit]


def get_unread_notification_count(user, *, website=None) -> int:
    """Return the count of a user's unread in-app notifications."""
    filters = {
        "user": user,
        "read": False,
        "notification__type": "in_app",
    }
    if website:
        filters["notification__website"] = website
    return NotificationsUserStatus.objects.filter(**filters).count()


def mark_notification_as_read(user, notification_id) -> bool:
    """Mark a single notification as read for a specific user."""
    try:
        row = NotificationsUserStatus.objects.get(
            user=user,
            notification_id=notification_id,
        )
        row.read = True
        row.read_at = timezone.now()
        row.save(update_fields=["read", "read_at"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(
            "NotificationUserStatus not found for user=%s, notif=%s",
            getattr(user, "id", None),
            notification_id,
        )
        return False


def bulk_mark_all_as_read(user, *, website=None) -> int:
    """Mark all unread in-app notifications as read for a user."""
    filters = {"user": user, "read": False}
    if website:
        filters["notification__website"] = website
    now = timezone.now()
    return (
        NotificationsUserStatus.objects.filter(**filters)
        .update(read=True, read_at=now)
    )


def pin_notification(user, notification_id) -> bool:
    """Pin one notification for a user."""
    try:
        row = NotificationsUserStatus.objects.get(
            user=user,
            notification_id=notification_id,
        )
        row.pinned = True
        row.save(update_fields=["pinned"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(
            "Pin failed: row missing (user=%s, notif=%s)",
            getattr(user, "id", None),
            notification_id,
        )
        return False


def unpin_notification(user, notification_id) -> bool:
    """Unpin one notification for a user."""
    try:
        row = NotificationsUserStatus.objects.get(
            user=user,
            notification_id=notification_id,
        )
        row.pinned = False
        row.save(update_fields=["pinned"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(
            "Unpin failed: row missing (user=%s, notif=%s)",
            getattr(user, "id", None),
            notification_id,
        )
        return False


def expire_old_notifications(user, *, older_than_days: int = 30) -> int:
    """Soft-expire in-app notifications older than N days for a user."""
    cutoff = timezone.now() - timezone.timedelta(days=older_than_days)
    updated = (
        NotificationsUserStatus.objects.filter(
            user=user,
            notification__type="in_app",
            notification__created_at__lt=cutoff,
            expires_at__isnull=True,
        ).update(expires_at=cutoff)
    )
    logger.info(
        "Soft-expired %s in-app notifications for user %s (>%s days).",
        updated,
        getattr(user, "id", None),
        older_than_days,
    )
    return updated


# -----------------------------
# Internal helpers (non-public)
# -----------------------------

def _create_user_notification_status(
    notification: Notification,
    users: Iterable,
) -> None:
    """Bulk-create per-user status rows for a notification.

    Args:
        notification: The Notification to attach.
        users: Iterable of user instances.
    """
    users = [u for u in users if getattr(u, "id", None)]
    if not users:
        return

    rows = [
        NotificationsUserStatus(
            user=u,
            notification=notification,
            read=False,
            pinned=False,
        )
        for u in users
    ]
    # Use ignore_conflicts to be resilient to rare duplicates.
    with transaction.atomic():
        NotificationsUserStatus.objects.bulk_create(
            rows,
            ignore_conflicts=True,
        )