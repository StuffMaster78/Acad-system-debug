"""
FileCleanupService - retention-policy enforcement for managed files.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from django.utils import timezone

log = logging.getLogger(__name__)


class FileCleanupService:

    DEFAULT_GRACE_DAYS = 30
    DEFAULT_QUARANTINE_DAYS = 7

    @classmethod
    def cleanup_expired(cls) -> int:
        from files_management.enums import FileLifecycleStatus
        from files_management.models import ManagedFile
        from files_management.services.storage_service import StorageService

        qs = ManagedFile.objects.filter(
            delete_after__lte=timezone.now(),
            lifecycle_status__in=[FileLifecycleStatus.ACTIVE, FileLifecycleStatus.ARCHIVED],
        )
        return cls._delete_batch(qs, StorageService, "expired")

    @classmethod
    def cleanup_soft_deleted(cls, grace_days: int = DEFAULT_GRACE_DAYS) -> int:
        from files_management.enums import FileLifecycleStatus
        from files_management.models import ManagedFile
        from files_management.services.storage_service import StorageService

        cutoff = timezone.now() - timedelta(days=grace_days)
        qs = ManagedFile.objects.filter(
            lifecycle_status=FileLifecycleStatus.DELETED,
            deleted_at__lte=cutoff,
        )
        return cls._delete_batch(qs, StorageService, "soft-deleted")

    @classmethod
    def cleanup_quarantined(cls, quarantine_days: int = DEFAULT_QUARANTINE_DAYS) -> int:
        from files_management.enums import FileLifecycleStatus
        from files_management.models import ManagedFile
        from files_management.services.storage_service import StorageService

        cutoff = timezone.now() - timedelta(days=quarantine_days)
        qs = ManagedFile.objects.filter(
            lifecycle_status=FileLifecycleStatus.QUARANTINED,
            scan_completed_at__lte=cutoff,
        )
        return cls._delete_batch(qs, StorageService, "quarantined")

    @classmethod
    def run_all(
        cls,
        grace_days: int = DEFAULT_GRACE_DAYS,
        quarantine_days: int = DEFAULT_QUARANTINE_DAYS,
    ) -> dict:
        expired = cls.cleanup_expired()
        soft = cls.cleanup_soft_deleted(grace_days)
        quar = cls.cleanup_quarantined(quarantine_days)
        log.info("FileCleanup: %d expired, %d soft-deleted, %d quarantined", expired, soft, quar)
        return {"expired_deleted": expired, "soft_deleted_purged": soft, "quarantined_deleted": quar}

    @staticmethod
    def _delete_batch(queryset, StorageService, label: str) -> int:
        count = 0
        for mf in queryset.iterator(chunk_size=50):
            try:
                StorageService.delete(mf, hard=True)
                count += 1
            except Exception as exc:
                log.error("FileCleanup [%s]: failed %s: %s", label, mf.uuid, exc)
        return count
