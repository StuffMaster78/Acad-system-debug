# notifications_system/tasks/maintenance.py
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def clear_stale_digests(before_days: int = 30) -> None:
    """Delete sent digest rows older than before_days. Run daily."""
    from notifications_system.services.digest_service import (
        DigestService
    )
    deleted = DigestService.clear_stale_digests(before_days=before_days)
    logger.info("clear_stale_digests: deleted %s rows.", deleted)


@shared_task
def rebuild_unread_counts() -> None:
    """
    Recalculate unread counts from source of truth.
    Run manually after data migrations or if counts drift.
    """
    from notifications_system.models.user_notification_meta import (
        UserNotificationMeta
    )
    from notifications_system.models.notifications_user_status import (
        NotificationsUserStatus
    )

    metas = UserNotificationMeta.objects.select_related('user', 'website').all()
    updated = 0

    for meta in metas.iterator():
        actual_count = NotificationsUserStatus.objects.filter(
            user=meta.user,
            website=meta.website,
            is_read=False,
        ).count()

        if meta.unread_count != actual_count:
            meta.unread_count = actual_count
            meta.save(update_fields=['unread_count', 'updated_at'])
            updated += 1

    logger.info("rebuild_unread_counts: updated %s meta rows.", updated)


@shared_task
def cleanup_processed_outbox(before_days: int = 7) -> None:
    """Delete processed outbox rows older than before_days. Run daily."""
    from notifications_system.models.outbox import Outbox

    threshold = timezone.now() - timedelta(days=before_days)
    deleted, _ = Outbox.objects.filter(
        status=Outbox.PROCESSED,
        processed_at__lt=threshold,
    ).delete()
    logger.info("cleanup_processed_outbox: deleted %s rows.", deleted)