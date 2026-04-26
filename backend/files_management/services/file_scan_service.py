from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from files_management.enums import FileLifecycleStatus, FileScanStatus
from files_management.models import FileScanResult, ManagedFile


class FileScanService:
    """
    Records file scan outcomes.

    This service supports antivirus checks, moderation scans, OCR based
    PII detection, file risk scoring, and future AI assisted analysis.

    The service does not perform scanning directly. It records results
    from scanners or background tasks.
    """

    @classmethod
    @transaction.atomic
    def mark_pending(
        cls,
        *,
        managed_file: ManagedFile,
        scan_type: str,
        provider: str = "",
        result_payload: dict | None = None,
    ) -> FileScanResult:
        """
        Mark a file scan as pending.
        """

        managed_file.scan_status = FileScanStatus.PENDING
        managed_file.save(update_fields=["scan_status", "updated_at"])

        return FileScanResult.objects.create(
            managed_file=managed_file,
            scan_type=scan_type,
            status=FileScanStatus.PENDING,
            provider=provider,
            result_payload=result_payload or {},
        )

    @classmethod
    @transaction.atomic
    def mark_passed(
        cls,
        *,
        managed_file: ManagedFile,
        scan_type: str,
        provider: str = "",
        summary: str = "",
        result_payload: dict | None = None,
    ) -> FileScanResult:
        """
        Record a passed file scan.
        """

        managed_file.scan_status = FileScanStatus.PASSED
        managed_file.save(update_fields=["scan_status", "updated_at"])

        return FileScanResult.objects.create(
            managed_file=managed_file,
            scan_type=scan_type,
            status=FileScanStatus.PASSED,
            provider=provider,
            summary=summary,
            result_payload=result_payload or {},
            scanned_at=timezone.now(),
        )

    @classmethod
    @transaction.atomic
    def mark_failed(
        cls,
        *,
        managed_file: ManagedFile,
        scan_type: str,
        provider: str = "",
        summary: str = "",
        result_payload: dict | None = None,
    ) -> FileScanResult:
        """
        Record a failed file scan and quarantine the file.
        """

        managed_file.scan_status = FileScanStatus.FAILED
        managed_file.lifecycle_status = FileLifecycleStatus.QUARANTINED
        managed_file.save(
            update_fields=[
                "scan_status",
                "lifecycle_status",
                "updated_at",
            ]
        )

        return FileScanResult.objects.create(
            managed_file=managed_file,
            scan_type=scan_type,
            status=FileScanStatus.FAILED,
            provider=provider,
            summary=summary,
            result_payload=result_payload or {},
            scanned_at=timezone.now(),
        )

    @classmethod
    @transaction.atomic
    def mark_flagged(
        cls,
        *,
        managed_file: ManagedFile,
        scan_type: str,
        provider: str = "",
        summary: str = "",
        result_payload: dict | None = None,
    ) -> FileScanResult:
        """
        Record a flagged scan result and quarantine the file.
        """

        managed_file.scan_status = FileScanStatus.FLAGGED
        managed_file.lifecycle_status = FileLifecycleStatus.QUARANTINED
        managed_file.save(
            update_fields=[
                "scan_status",
                "lifecycle_status",
                "updated_at",
            ]
        )

        return FileScanResult.objects.create(
            managed_file=managed_file,
            scan_type=scan_type,
            status=FileScanStatus.FLAGGED,
            provider=provider,
            summary=summary,
            result_payload=result_payload or {},
            scanned_at=timezone.now(),
        )

    @classmethod
    @transaction.atomic
    def mark_error(
        cls,
        *,
        managed_file: ManagedFile,
        scan_type: str,
        provider: str = "",
        summary: str = "",
        result_payload: dict | None = None,
    ) -> FileScanResult:
        """
        Record a scanner error without assuming the file is safe.
        """

        managed_file.scan_status = FileScanStatus.ERROR
        managed_file.save(update_fields=["scan_status", "updated_at"])

        return FileScanResult.objects.create(
            managed_file=managed_file,
            scan_type=scan_type,
            status=FileScanStatus.ERROR,
            provider=provider,
            summary=summary,
            result_payload=result_payload or {},
            scanned_at=timezone.now(),
        )

    @classmethod
    @transaction.atomic
    def release_from_quarantine(
        cls,
        *,
        managed_file: ManagedFile,
        released_by,
        summary: str = "",
    ) -> ManagedFile:
        """
        Release a quarantined file after staff review.
        """

        is_staff = bool(
            getattr(released_by, "is_staff", False)
            or getattr(released_by, "is_superuser", False)
            or getattr(released_by, "is_admin", False)
        )

        if not is_staff:
            raise PermissionError(
                "Only staff can release a quarantined file."
            )

        managed_file.lifecycle_status = FileLifecycleStatus.ACTIVE
        managed_file.scan_status = FileScanStatus.PASSED

        metadata = dict(managed_file.metadata or {})
        metadata["quarantine_release"] = {
            "released_by_id": getattr(released_by, "id", None),
            "summary": summary,
            "released_at": timezone.now().isoformat(),
        }
        managed_file.metadata = metadata

        managed_file.full_clean()
        managed_file.save(
            update_fields=[
                "lifecycle_status",
                "scan_status",
                "metadata",
                "updated_at",
            ]
        )

        return managed_file