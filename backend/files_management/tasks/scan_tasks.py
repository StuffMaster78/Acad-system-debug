from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from files_management.enums import FileLifecycleStatus, FileScanStatus
from files_management.models.managed_file import ManagedFile

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scan_file_for_viruses(self, managed_file_id: int) -> None:
    """
    Scan a managed file for viruses.

    For now this is a safe placeholder. Later, plug in ClamAV here.
    """

    try:
        managed_file = ManagedFile.objects.get(pk=managed_file_id)
    except ManagedFile.DoesNotExist:
        logger.warning(
            "Virus scan skipped. ManagedFile %s does not exist.",
            managed_file_id,
        )
        return

    if managed_file.lifecycle_status == FileLifecycleStatus.DELETED:
        return

    try:
        managed_file.scan_status = FileScanStatus.CLEAN
        managed_file.scanned_at = timezone.now()
        managed_file.lifecycle_status = FileLifecycleStatus.ACTIVE
        managed_file.save(
            update_fields=[
                "scan_status",
                "scanned_at",
                "lifecycle_status",
                "updated_at",
            ]
        )

    except Exception as exc:
        logger.exception(
            "Virus scan failed for ManagedFile %s.",
            managed_file_id,
        )
        raise self.retry(exc=exc) from exc