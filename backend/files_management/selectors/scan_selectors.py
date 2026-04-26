from __future__ import annotations

from django.db.models import QuerySet

from files_management.models import FileProcessingJob, FileScanResult


class FileScanSelector:
    """
    Read helpers for scan and processing records.
    """

    @staticmethod
    def scans_for_file(*, managed_file) -> QuerySet[FileScanResult]:
        """
        Return scan results for a managed file.
        """

        return FileScanResult.objects.filter(
            managed_file=managed_file,
        )

    @staticmethod
    def latest_scan_for_file(
        *,
        managed_file,
        scan_type: str,
    ) -> FileScanResult | None:
        """
        Return the latest scan result for a file and scan type.
        """

        return FileScanResult.objects.filter(
            managed_file=managed_file,
            scan_type=scan_type,
        ).order_by("-created_at").first()

    @staticmethod
    def processing_jobs_for_file(
        *,
        managed_file,
    ) -> QuerySet[FileProcessingJob]:
        """
        Return processing jobs for a managed file.
        """

        return FileProcessingJob.objects.filter(
            managed_file=managed_file,
        )

    @staticmethod
    def latest_processing_job(
        *,
        managed_file,
        job_type: str,
    ) -> FileProcessingJob | None:
        """
        Return the latest processing job for a file and job type.
        """

        return FileProcessingJob.objects.filter(
            managed_file=managed_file,
            job_type=job_type,
        ).order_by("-created_at").first()