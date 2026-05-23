"""
Virus scanning tasks.
Triggered per-file on upload by StorageService.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def scan_file_for_viruses(self, managed_file_id: int):
    """
    Scan a single file for viruses via ClamAV.

    Called immediately after upload.  Retries on transient failure.
    On infection: file is quarantined and admins are notified.
    """
    from files_management.models import ManagedFile
    from files_management.services.virus_scan_service import VirusScanService

    try:
        managed_file = ManagedFile.objects.get(pk=managed_file_id)
    except ManagedFile.DoesNotExist:
        logger.error("Scan task: ManagedFile %s not found", managed_file_id)
        return {"error": "File not found"}

    result = VirusScanService.scan_file(managed_file)

    if result["status"] == "infected":
        _notify_infected_file(managed_file, result)

    elif result["status"] == "scan_error":
        raise self.retry(exc=RuntimeError(result["detail"]))

    return {
        "file_id": managed_file_id,
        "uuid": str(managed_file.uuid),
        "status": result["status"],
        "detail": result["detail"],
    }


def _notify_infected_file(managed_file, scan_result: dict):
    """Send notification when an infected file is detected."""
    logger.critical(
        "INFECTED FILE DETECTED: %s (%s) uploaded by %s — %s",
        managed_file.uuid,
        managed_file.original_filename,
        managed_file.uploaded_by,
        scan_result.get("detail", "unknown"),
    )

    # Notify via the platform's notification system
    try:
        from notifications_system.services.notification_service import (
            NotificationService,
        )
        from notifications_system.enums import NotificationPriority

        # Notify the uploader (if they're a real user)
        if managed_file.uploaded_by:
            NotificationService.notify(
                event_key="file.infected_detected",
                recipient=managed_file.uploaded_by,
                website=managed_file.website,
                context={
                    "filename": managed_file.original_filename,
                    "uuid": str(managed_file.uuid),
                    "scan_detail": scan_result.get("detail", "unknown"),
                },
                priority=NotificationPriority.CRITICAL,
                is_critical=True,
            )

        # Notify all staff on this website
        NotificationService.notify_staff(
            event_key="file.infected_detected",
            website=managed_file.website,
            context={
                "filename": managed_file.original_filename,
                "uuid": str(managed_file.uuid),
                "uploaded_by": str(managed_file.uploaded_by),
                "scan_detail": scan_result.get("detail", "unknown"),
            },
            priority=NotificationPriority.CRITICAL,
        )

    except ImportError:
        logger.debug(
            "notifications_system not available — "
            "infected file alert logged only"
        )
    except Exception as exc:
        logger.warning("Could not send infected file notification: %s", exc)