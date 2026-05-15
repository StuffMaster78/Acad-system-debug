"""
writer_management/tasks/availability_tasks.py

Celery tasks for availability maintenance.

Two tasks:

    cleanup_expired_windows
        Deletes WriterAvailabilityWindow rows whose end_at has passed.
        Run every hour via Celery Beat.

    process_auto_offline
        Sets WriterStatus to OFFLINE for writers who have been
        inactive longer than their auto_offline_after_minutes setting.
        Run every 5 minutes via Celery Beat.

CELERY BEAT SCHEDULE (add to settings.py):

    from celery.schedules import crontab

    CELERY_BEAT_SCHEDULE = {
        "cleanup-expired-availability-windows": {
            "task": "writer_management.tasks.availability_tasks"
                    ".cleanup_expired_windows",
            "schedule": crontab(minute=0),  # every hour
        },
        "process-writer-auto-offline": {
            "task": "writer_management.tasks.availability_tasks"
                    ".process_auto_offline",
            "schedule": crontab(minute="*/5"),  # every 5 minutes
        },
    }
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

logger = logging.getLogger(__name__)


@shared_task(
    name="writer_management.tasks.availability_tasks.cleanup_expired_windows",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def cleanup_expired_windows(self):
    """
    Delete WriterAvailabilityWindow rows whose end_at has passed.

    Safe to run multiple times — idempotent.
    Does not affect windows with end_at=None (indefinite).

    Returns dict with count of deleted rows for monitoring.
    """
    from writer_management.models.writer_availability import WriterAvailabilityWindow

    try:
        deleted, _ = WriterAvailabilityWindow.objects.filter(
            end_at__lt=now()
        ).delete()

        logger.info(
            "cleanup_expired_windows: deleted %d expired windows.",
            deleted,
        )
        return {"deleted_windows": deleted}

    except Exception as exc:
        logger.exception("cleanup_expired_windows failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(
    name="writer_management.tasks.availability_tasks.process_auto_offline",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def process_auto_offline(self):
    """
    Set WriterStatus to OFFLINE for writers who have been inactive
    longer than their WriterAvailabilityPreference.auto_offline_after_minutes.

    Only applies when:
        preference.auto_go_offline is True
        WriterStatus.status is ONLINE or AWAY
        WriterStatus.last_seen_at is older than the threshold

    Does NOT affect routing eligibility — offline writers remain
    eligible for queued assignments.
    """
    from writer_management.models.writer_availability import WriterAvailabilityPreference
    from writer_management.models.writer_status import WriterStatus
    from writer_management.enums import WriterOnlineStatus

    try:
        n = now()
        processed = 0
        set_offline = 0

        active_prefs = (
            WriterAvailabilityPreference.objects
            .filter(auto_go_offline=True)
            .select_related("writer__status")
        )

        for pref in active_prefs:
            processed += 1

            try:
                status = pref.writer.status
            except WriterStatus.DoesNotExist:
                continue

            if status.status not in (
                WriterOnlineStatus.ONLINE,
                WriterOnlineStatus.AWAY,
            ):
                continue

            if status.last_seen_at is None:
                continue

            threshold = timedelta(minutes=pref.auto_offline_after_minutes)
            if (n - status.last_seen_at) >= threshold:
                status.mark_offline()
                set_offline += 1

        logger.info(
            "process_auto_offline: checked=%d set_offline=%d",
            processed,
            set_offline,
        )
        return {"processed": processed, "set_offline": set_offline}

    except Exception as exc:
        logger.exception("process_auto_offline failed: %s", exc)
        raise self.retry(exc=exc)