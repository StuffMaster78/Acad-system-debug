from django.db import models

from files_management.enums import FileScanStatus


class FileScanResult(models.Model):
    """
    Stores scan results for a managed file.

    This model supports future antivirus checks, malware detection,
    content moderation, OCR based PII checks, and document risk scoring.
    It is intentionally generic because scanning tools may change.
    """

    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="scan_results",
    )

    scan_type = models.CharField(
        max_length=80,
        help_text="Example values: antivirus, pii, moderation, ocr.",
    )

    status = models.CharField(
        max_length=32,
        choices=FileScanStatus.choices,
        default=FileScanStatus.PENDING,
    )

    provider = models.CharField(
        max_length=120,
        blank=True,
        help_text="External or internal scanner name.",
    )

    summary = models.TextField(
        blank=True,
    )

    result_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw scanner result or normalized metadata.",
    )

    scanned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["managed_file", "scan_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["scanned_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.managed_file.pk}: {self.scan_type} {self.status}"