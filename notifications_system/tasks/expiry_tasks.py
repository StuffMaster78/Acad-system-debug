from celery import shared_task # type: ignore
import logging
from notifications_system.services.notification_expiry_service import (
    NotificationExpiryService
)
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def soft_expire_user_notifications(user_id, older_than_days=30):
    """
    Soft-expires in-app notifications for a given user.
    """
    from notifications_system.models import User  # Delay import to avoid circular dependency

    try:
        user = User.objects.get(pk=user_id)
        NotificationExpiryService.soft_expire_old_notifications(
            user, older_than_days
        )
        logger.info(
            f"[soft_expire_user_notifications] Expired old notifications for user {user_id}"
        )
    except User.DoesNotExist:
        logger.warning(f"User {user_id} not found for soft expiry task.")
    except Exception as e:
        logger.exception(f"Error expiring notifications for user {user_id}: {e}")


@shared_task
def purge_expired_notifications_task(older_than_days=90, dry_run=False):
    """
    Globally purges expired in-app notifications.
    """
    try:
        deleted_count = NotificationExpiryService.purge_expired_notifications(
            older_than_days=older_than_days,
            dry_run=dry_run
        )
        logger.info(f"[purge_expired_notifications_task] Deleted {deleted_count} expired notifications.")
        return deleted_count
    except Exception as e:
        logger.exception("Error during expired notification purge.")
        return 0