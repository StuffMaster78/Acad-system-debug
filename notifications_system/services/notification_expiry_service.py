"""Utilities to expire and purge old in-app notifications."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional

from django.utils import timezone

from notifications_system.models.notifications_user_status import (
    NotificationsUserStatus,
)

logger = logging.getLogger(__name__)


class NotificationExpiryService:
    """Expire and purge per-user notification status records."""

    DEFAULT_SOFT_DAYS = 30
    DEFAULT_PURGE_DAYS = 90
    DEFAULT_CHANNEL_FIELD = "type"     # change to "channel" if needed
    DEFAULT_INAPP_VALUE = "in_app"

    @classmethod
    def soft_expire_old_notifications(
        cls,
        user,
        older_than_days: int = DEFAULT_SOFT_DAYS,
        channel_field: str = DEFAULT_CHANNEL_FIELD,
        in_app_value: str = DEFAULT_INAPP_VALUE,
    ) -> int:
        """Mark old in-app notifications as expired (soft expire).

        Sets ``expires_at`` on records older than the cutoff.

        Args:
            user: Target user instance.
            older_than_days: Age threshold in days (default: 30).
            channel_field: Field name holding the channel (e.g. "type").
            in_app_value: Value that represents in-app channel.

        Returns:
            Number of rows updated.
        """
        cutoff = timezone.now() - timedelta(days=older_than_days)

        qs = NotificationsUserStatus.objects.filter(
            user=user,
            created_at__lt=cutoff,
            expires_at__isnull=True,
        )
        # Apply channel filter dynamically to avoid hardcoding model shape.
        qs = qs.filter(**{channel_field: in_app_value})

        updated = qs.update(expires_at=cutoff)

        logger.info(
            "Soft-expired %d notifications for user %s older than %d days.",
            updated,
            getattr(user, "id", user),
            older_than_days,
        )
        return int(updated)

    @classmethod
    def purge_expired_notifications(
        cls,
        older_than_days: int = DEFAULT_PURGE_DAYS,
        dry_run: bool = False,
        website_id: Optional[int] = None,
    ) -> int:
        """Hard delete notifications whose ``expires_at`` is very old.

        Args:
            older_than_days: Delete items expired before this many days.
            dry_run: If True, only count what would be deleted.
            website_id: Optional tenant filter if your model has it.

        Returns:
            Number of rows deleted (or counted in dry_run mode).
        """
        cutoff = timezone.now() - timedelta(days=older_than_days)

        qs = NotificationsUserStatus.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=cutoff,
        )
        if website_id is not None and hasattr(
            NotificationsUserStatus, "website_id"
        ):
            qs = qs.filter(website_id=website_id)

        count = qs.count()
        if dry_run:
            logger.info(
                "[dry-run] Would delete %d expired notifications "
                "older than %d days%s.",
                count,
                older_than_days,
                f" (website_id={website_id})" if website_id else "",
            )
            return int(count)

        deleted, _ = qs.delete()
        logger.info(
            "Hard-deleted %d expired notifications older than %d days%s.",
            deleted,
            older_than_days,
            f" (website_id={website_id})" if website_id else "",
        )
        return int(deleted)