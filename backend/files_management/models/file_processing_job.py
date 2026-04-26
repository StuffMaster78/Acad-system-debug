from django.db import models

from files_management.enums import FileProcessingStatus


class FileProcessingJob(models.Model):
    """
    Tracks background file processing work.

    Examples include thumbnail generation, PDF preview extraction,
    OCR, video metadata extraction, compression, and future embedding
    preparation for AI assisted workflows.
    """

    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="processing_jobs",
    )

    job_type = models.CharField(
        max_length=80,
        help_text="Example values: thumbnail, preview, ocr, compress.",
    )

    status = models.CharField(
        max_length=32,
        choices=FileProcessingStatus.choices,
        default=FileProcessingStatus.PENDING,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    last_error = models.TextField(
        blank=True,
    )

    input_payload = models.JSONField(
        default=dict,
        blank=True,
    )

    output_payload = models.JSONField(
        default=dict,
        blank=True,
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["managed_file", "job_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.managed_file.id}: {self.job_type} {self.status}"