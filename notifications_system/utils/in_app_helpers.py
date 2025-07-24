import logging
from django.utils import timezone
from django.db.models import Case, When, IntegerField
from notifications_system.services.preferences import NotificationPreferenceResolver
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.models.notifications import Notification
from django.db.models import Q

import users

logger = logging.getLogger(__name__)


def send_in_app_notification(
    user,
    title: str,
    message: str,
    *,
    website=None,
    event_key=None,
    role=None,
    data: dict = None,
    expires_at=None,
    priority='normal',
    metadata: dict = None,
):
    """
    Creates a Notification and user-specific NotificationUserStatus for in-app delivery.
    """

    try:
        notification = Notification.objects.create(
            title=title,
            message=message,
            type="in_app",
            website=website,
            event_key=event_key,
            role=role,
            data=data or {},
            metadata=metadata or {},
            priority=priority,
            expires_at=expires_at,
            delivery_channels=["in_app"],  # Make sure you track this
        )

        # Create per-user notification status
        create_user_notification_status(
            notification, [user]
        )

        logger.info(
            f"In-app notification created for user {user.id} with event: {event_key}"
        )

        return notification

    except Exception as e:
        logger.error(f"Failed to create in-app notification for user {user.id}: {e}")
        return None

def send_bulk_in_app_notification(
    users,
    title: str,
    message: str,
    *,
    website=None,
    event_key=None,
    role=None,
    data: dict = None,
    expires_at=None,
    priority='normal',
    metadata: dict = None,
):
    """
    Sends a single in-app notification to multiple users.
    """
    if not users:
        logger.warning("No users provided for bulk in-app notification.")
        return None

    try:
        notification = Notification.objects.create(
            title=title,
            message=message,
            type="in_app",
            website=website,
            event_key=event_key,
            role=role,
            data=data or {},
            metadata=metadata or {},
            priority=priority,
            expires_at=expires_at,
            delivery_channels=["in_app"],
        )

        create_user_notification_status(notification, users)

        logger.info(
            f"In-app notification sent to {len(users)} users with event: {event_key}"
        )
        return notification

    except Exception as e:
        logger.error(f"Failed to send bulk in-app notification: {e}")
        return None

def get_user_notifications(
    user, *, website=None, include_read=False
):
    qs = NotificationsUserStatus.objects.filter(user=user)

    if website:
        qs = qs.filter(notification__website=website)

    if not include_read:
        qs = qs.filter(read=False)

    return qs.select_related('notification').order_by('-notification__created_at')

def get_unread_notification_count(
        user, *, website=None
):
    qs = NotificationsUserStatus.objects.filter(user=user, read=False)
    if website:
        qs = qs.filter(notification__website=website)
    return qs.count()

def mark_notification_as_read(
        user, notification_id
):
    try:
        notif_status = NotificationsUserStatus.objects.get(
            user=user, notification_id=notification_id
        )
        notif_status.read = True
        notif_status.read_at = timezone.now()
        notif_status.save(update_fields=["read", "read_at"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(
            f"NotificationUserStatus not found for user={user.id}, notification={notification_id}"
        )
        return False
    
def bulk_mark_all_as_read(user, *, website=None):
    qs = NotificationsUserStatus.objects.filter(user=user, read=False)
    if website:
        qs = qs.filter(notification__website=website)

    now = timezone.now()
    updated_count = qs.update(read=True, read_at=now)
    return updated_count

def pin_notification(
        user, notification_id
):
    try:
        notif_status = NotificationsUserStatus.objects.get(
            user=user, notification_id=notification_id
        )
        notif_status.pinned = True
        notif_status.save(update_fields=["pinned"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(
            f"Pin failed — NotificationUserStatus not found for user={user.id}, notification={notification_id}"
        )
        return False


def unpin_notification(
        user, notification_id
):
    try:
        notif_status = NotificationsUserStatus.objects.get(
            user=user, notification_id=notification_id
        )
        notif_status.pinned = False
        notif_status.save(update_fields=["pinned"])
        return True
    except NotificationsUserStatus.DoesNotExist:
        logger.warning(f"Unpin failed — NotificationUserStatus not found for user={user.id}, notification={notification_id}")
        return False


def get_pinned_notifications(
        user, *, website=None
):
    qs = NotificationsUserStatus.objects.filter(
        user=user, pinned=True
    )
    if website:
        qs = qs.filter(notification__website=website)
    return qs.select_related("notification").order_by("-notification__created_at")


def create_user_notification_status(
        notification: Notification, users: list
):
    """
    Bulk-create NotificationUserStatus records for each user for a notification,
    using the existing resolver logic to respect preferences.
    """
    if not users:
        return

    resolver = NotificationPreferenceResolver()
    resolver.create_user_status_records(notification, users)


def expire_old_notifications(
        user, older_than_days: int = 30
):
    """
    Expires in-app notifications older than the
    specified number of days for a specific user.
    """
    cutoff = timezone.now() - timezone.timedelta(
        days=older_than_days
    )

    expired = NotificationsUserStatus.objects.filter(
        user=user,
        notification__type="in_app",
        notification__created_at__lt=cutoff,
        expires_at__isnull=True
    ).update(expires_at=cutoff)

    logger.info(
        f"Expired {expired} in-app notifications for user {user.id} older than {older_than_days} days."
    )
    return expired



def get_user_notifications(
        user, website=None, limit=50, offset=0
):
    """
    Fetches in-app notifications for a specific user, sorted by:
    1. Pinned first
    2. Priority (critical > high > normal > low)
    3. Most recent
    Uses NotificationsUserStatus for per-user tracking.
    """

    filters = {
        "user": user,
        "notification__type": "in_app",
    }

    if website:
        filters["notification__website"] = website

    priority_order = Case(
        When(notification__priority="critical", then=1),
        When(notification__priority="high", then=2),
        When(notification__priority="normal", then=3),
        When(notification__priority="low", then=4),
        default=5,
        output_field=IntegerField(),
    )

    queryset = NotificationsUserStatus.objects.select_related("notification") \
        .filter(**filters) \
        .order_by(
            "-pinned",
            priority_order,
            "-notification__created_at"
        )[offset:offset + limit]

    return queryset


def get_unread_notification_count(user, website=None):
    """
    Returns the count of unread in-app notifications for a specific user.
    """
    filters = {
        "user": user,
        "read": False,
        "notification__type": "in_app",
    }

    if website:
        filters["notification__website"] = website

    count = NotificationsUserStatus.objects.filter(**filters).count()
    logger.debug(f"User {user.id} has {count} unread in-app notifications")
    return count





