# notifications/services/notification_expiry_service.py

from django.utils import timezone
from datetime import timedelta
import logging

from notifications_system.models.notifications_user_status import NotificationsUserStatus

logger = logging.getLogger(__name__)


class NotificationExpiryService:

    @classmethod
    def soft_expire_old_notifications(cls, user, older_than_days: int = 30):
        """
        Marks old in-app notifications as expired by setting `expires_at`.
        """
        cutoff = timezone.now() - timedelta(days=older_than_days)
        updated = NotificationsUserStatus.objects.filter(
            user=user,
            type="in_app",
            created_at__lt=cutoff,
            expires_at__isnull=True
        ).update(expires_at=cutoff)

        logger.info(f"Soft-expired {updated} notifications for user {user.id} older than {older_than_days} days.")
        return updated

    @classmethod
    def purge_expired_notifications(
        cls, older_than_days: int = 90, dry_run=False
    ):
        """
        Hard deletes notifications that have been
        expired for longer than `older_than_days`.
        """
        cutoff = timezone.now() - timedelta(days=older_than_days)
        queryset = NotificationsUserStatus.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=cutoff
        )

        count = queryset.count()
        if dry_run:
            logger.info(
                f"[Dry Run] Would delete {count} expired notifications older than {older_than_days} days."
            )
            return count

        deleted_count, _ = queryset.delete()
        logger.info(
            f"Hard-deleted {deleted_count} expired notifications older than {older_than_days} days."
        )
        return deleted_count