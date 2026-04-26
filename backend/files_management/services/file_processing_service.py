from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from files_management.enums import FileProcessingStatus
from files_management.models import FileProcessingJob, ManagedFile


class FileProcessingService:
    """
    Manages background processing jobs for files.

    Processing jobs represent asynchronous work such as thumbnail
    creation, PDF preview extraction, OCR, media metadata extraction,
    compression, and future AI preparation.

    This service only tracks job state. Celery tasks or worker services
    should perform the actual processing.
    """

    @classmethod
    @transaction.atomic
    def create_job(
        cls,
        *,
        managed_file: ManagedFile,
        job_type: str,
        input_payload: dict | None = None,
        scheduled_at=None,
    ) -> FileProcessingJob:
        """
        Create a pending processing job for a file.
        """

        return FileProcessingJob.objects.create(
            managed_file=managed_file,
            job_type=job_type,
            status=FileProcessingStatus.PENDING,
            input_payload=input_payload or {},
            scheduled_at=scheduled_at,
        )

    @classmethod
    @transaction.atomic
    def mark_running(
        cls,
        *,
        job: FileProcessingJob,
    ) -> FileProcessingJob:
        """
        Mark a processing job as running.
        """

        job.status = FileProcessingStatus.RUNNING
        job.started_at = timezone.now()
        job.attempts += 1
        job.full_clean()
        job.save(
            update_fields=[
                "status",
                "started_at",
                "attempts",
                "updated_at",
            ]
        )

        return job

    @classmethod
    @transaction.atomic
    def mark_succeeded(
        cls,
        *,
        job: FileProcessingJob,
        output_payload: dict | None = None,
    ) -> FileProcessingJob:
        """
        Mark a processing job as successful.
        """

        job.status = FileProcessingStatus.SUCCEEDED
        job.completed_at = timezone.now()
        job.output_payload = output_payload or {}
        job.last_error = ""
        job.full_clean()
        job.save(
            update_fields=[
                "status",
                "completed_at",
                "output_payload",
                "last_error",
                "updated_at",
            ]
        )

        return job

    @classmethod
    @transaction.atomic
    def mark_failed(
        cls,
        *,
        job: FileProcessingJob,
        error_message: str,
        output_payload: dict | None = None,
    ) -> FileProcessingJob:
        """
        Mark a processing job as failed.
        """

        job.status = FileProcessingStatus.FAILED
        job.completed_at = timezone.now()
        job.last_error = error_message
        job.output_payload = output_payload or {}
        job.full_clean()
        job.save(
            update_fields=[
                "status",
                "completed_at",
                "last_error",
                "output_payload",
                "updated_at",
            ]
        )

        return job

    @classmethod
    @transaction.atomic
    def cancel_job(
        cls,
        *,
        job: FileProcessingJob,
        reason: str = "",
    ) -> FileProcessingJob:
        """
        Cancel a pending or running processing job.
        """

        job.status = FileProcessingStatus.CANCELLED
        job.completed_at = timezone.now()
        job.last_error = reason
        job.full_clean()
        job.save(
            update_fields=[
                "status",
                "completed_at",
                "last_error",
                "updated_at",
            ]
        )

        return job