from django.conf import settings
from django.db import models

from files_management.enums import (
    FileKind,
    FileLifecycleStatus,
    FileScanStatus,
)


class ManagedFile(models.Model):
    """
    Represents a stored file within the system.

    This model contains storage metadata and lifecycle information.
    It does NOT contain business logic related to orders, messages,
    or CMS usage.

    Files are linked to domain objects through FileAttachment.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="managed_files",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )

    file = models.FileField(
        upload_to="managed-files/%Y/%m/%d/",
        help_text="Underlying file stored in configured storage.",
    )

    original_name = models.CharField(
        max_length=255,
        help_text="Original filename as uploaded by the user.",
    )

    file_size = models.BigIntegerField(
        help_text="Size of the file in bytes.",
    )

    mime_type = models.CharField(
        max_length=255,
        help_text="Detected MIME type of the file.",
    )

    file_kind = models.CharField(
        max_length=32,
        choices=FileKind.choices,
        default=FileKind.OTHER,
    )

    checksum = models.CharField(
        max_length=128,
        blank=True,
        help_text="Optional checksum for integrity verification.",
    )

    lifecycle_status = models.CharField(
        max_length=32,
        choices=FileLifecycleStatus.choices,
        default=FileLifecycleStatus.ACTIVE,
    )

    scan_status = models.CharField(
        max_length=32,
        choices=FileScanStatus.choices,
        default=FileScanStatus.NOT_SCANNED,
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Indicates if file can be publicly accessed.",
    )

    storage_key = models.CharField(
        max_length=500,
        help_text="Path/key used in storage backend (S3/DO/local).",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible metadata (dimensions, duration, etc).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "file_kind"]),
            models.Index(fields=["lifecycle_status"]),
            models.Index(fields=["scan_status"]),
        ]

    def __str__(self) -> str:
        return self.original_name