import logging
from celery import shared_task # type: ignore
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import NotificationsUserStatus
   

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def expire_stale_in_app_notifications_per_user(days_old=30):
    """Expire in-app notifications that are older than a specified number of days.
    This task runs for each user and marks notifications as expired
    if they are older than the specified number of days.
    Args:
        days_old (int): Number of days after which notifications should be expired.
    Returns:
        int: Total number of notifications expired.
    """
    cutoff = now() - timedelta(days=days_old)
    total_expired = 0

    for user in User.objects.all():
        count = NotificationsUserStatus.objects.filter(
            user=user,
            notification__type="in_app",
            notification__created_at__lt=cutoff,
            expires_at__isnull=True
        ).update(expires_at=cutoff)
        total_expired += count
        if count > 0:
            logger.info(f"[User Expiry] Expired {count} for user {user.id}")
    
    logger.info(f"[Total] Expired {total_expired} stale in-app notifications across all users.")
    return total_expired
