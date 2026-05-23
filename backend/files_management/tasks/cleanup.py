"""
File cleanup tasks.
Runs nightly to enforce retention policies and purge old files.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_files():
    """
    Delete files past their retention date.

    Three categories cleaned up:
    1. Retention-expired: files with delete_after in the past
    2. Soft-deleted: files marked deleted >30 days ago (grace period)
    3. Quarantined: infected files >7 days old

    Run nightly via Celery beat.
    """
    from files_management.enums import FileLifecycleStatus
    from files_management.models import ManagedFile
    from files_management.services.storage_service import StorageService

    now = timezone.now()

    # 1. Files with explicit delete_after that's passed
    expired = ManagedFile.objects.filter(
        delete_after__lte=now,
        lifecycle_status__in=[
            FileLifecycleStatus.ACTIVE,
            FileLifecycleStatus.ARCHIVED,
        ],
    )

    expired_count = 0
    for managed_file in expired.iterator(chunk_size=50):
        try:
            StorageService.delete(managed_file, hard=True)
            expired_count += 1
        except Exception as exc:
            logger.error(
                "Failed to delete expired file %s: %s",
                managed_file.uuid,
                exc,
            )

    # 2. Soft-deleted files older than 30 days (grace period)
    grace_cutoff = now - timezone.timedelta(days=30)
    soft_deleted = ManagedFile.objects.filter(
        lifecycle_status=FileLifecycleStatus.DELETED,
        deleted_at__lte=grace_cutoff,
    )

    soft_count = 0
    for managed_file in soft_deleted.iterator(chunk_size=50):
        try:
            StorageService.delete(managed_file, hard=True)
            soft_count += 1
        except Exception as exc:
            logger.error(
                "Failed to hard-delete soft-deleted file %s: %s",
                managed_file.uuid,
                exc,
            )

    # 3. Quarantined (infected) files older than 7 days
    quarantine_cutoff = now - timezone.timedelta(days=7)
    quarantined = ManagedFile.objects.filter(
        lifecycle_status=FileLifecycleStatus.QUARANTINED,
        scan_completed_at__lte=quarantine_cutoff,
    )

    quarantine_count = 0
    for managed_file in quarantined.iterator(chunk_size=50):
        try:
            StorageService.delete(managed_file, hard=True)
            quarantine_count += 1
        except Exception as exc:
            logger.error(
                "Failed to delete quarantined file %s: %s",
                managed_file.uuid,
                exc,
            )

    logger.info(
        "File cleanup complete: %d expired, %d soft-deleted, %d quarantined",
        expired_count,
        soft_count,
        quarantine_count,
    )

    return {
        "expired_deleted": expired_count,
        "soft_deleted_purged": soft_count,
        "quarantined_deleted": quarantine_count,
    }