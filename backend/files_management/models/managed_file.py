"""
ManagedFile — THE canonical file record.

Every uploaded file — CMS images, attachments, order files, writer
deliverables, avatars — has one of these. Other apps reference this
via FK, never store file paths directly.

Business domains such as orders, CMS, messages, classes, avatars,
and special orders should reference this model instead of storing
raw file paths directly.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from files_management.models.file_bucket import FileBucket
from files_management.enums import (
    FileKind,
    FileLifecycleStatus,
    FileScanStatus,
)


class ManagedFile(models.Model):
    """
    Canonical file record for every stored file in the system.

    This model owns storage metadata, scan state, lifecycle state,
    file identity, derivative tracking, retention rules, and access
    counters.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="managed_files",
    )

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.SET_NULL,
        related_name="managed_files",
        null=True,
        blank=True,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )

    bucket = models.ForeignKey(
        FileBucket,
        on_delete=models.PROTECT,
        related_name="files",
    )

    file = models.FileField(
        upload_to="managed-files/%Y/%m/%d/",
        help_text="Underlying file stored in the configured storage backend.",
    )

    storage_key = models.CharField(
        max_length=500,
        unique=True,
        help_text="Full path or object key in the storage backend.",
    )

    original_filename = models.CharField(
        max_length=255,
        help_text="Original filename as uploaded by the user.",
    )

    file_size_bytes = models.BigIntegerField(
        help_text="Size of the file in bytes.",
    )

    mime_type = models.CharField(
        max_length=255,
        help_text="Detected MIME type of the file.",
    )

    file_extension = models.CharField(
        max_length=20,
        blank=True,
        help_text="Normalised file extension without the leading dot.",
    )

    file_kind = models.CharField(
        max_length=32,
        choices=FileKind.choices,
        default=FileKind.OTHER,
        db_index=True,
    )

    sha256_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash of file contents for integrity and deduplication.",
    )

    checksum = models.CharField(
        max_length=128,
        blank=True,
        help_text="Optional secondary checksum for integrity verification.",
    )

    # Image / PDF / media metadata
    width_px = models.PositiveIntegerField(null=True, blank=True)
    height_px = models.PositiveIntegerField(null=True, blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    # Virus / malware scan
    scan_status = models.CharField(
        max_length=32,
        choices=FileScanStatus.choices,
        default=FileScanStatus.NOT_SCANNED,
        db_index=True,
    )
    scan_completed_at = models.DateTimeField(null=True, blank=True)
    scan_engine = models.CharField(max_length=50, blank=True)
    scan_result_detail = models.TextField(blank=True)
    scanned_at = models.DateTimeField(null=True, blank=True)

    # Lifecycle
    lifecycle_status = models.CharField(
        max_length=32,
        choices=FileLifecycleStatus.choices,
        default=FileLifecycleStatus.ACTIVE,
        db_index=True,
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Whether this file is allowed to be publicly accessible.",
    )

    # Generic association (any model can own this file)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Derivatives (thumbnails, WebP, previews)
    parent_file = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="derivatives",
    )
    derivative_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("", "Original"),
            ("thumbnail_sm", "Small thumbnail"),
            ("thumbnail_md", "Medium thumbnail"),
            ("thumbnail_lg", "Large thumbnail"),
            ("preview_pdf", "PDF preview"),
            ("optimized", "Optimised version"),
            ("webp", "WebP version"),
        ],
    )

    # Retention
    retention_policy = models.CharField(
        max_length=30,
        choices=[
            ("forever", "Keep forever"),
            ("30_days", "Delete after 30 days"),
            ("90_days", "Delete after 90 days"),
            ("1_year", "Delete after 1 year"),
            ("order_complete_30", "30 days after order completion"),
            ("order_complete_90", "90 days after order completion"),
        ],
        default="forever",
    )
    delete_after = models.DateTimeField(null=True, blank=True)

    # Usage
    download_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    # Flexible metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible metadata such as dimensions, duration, or parser output.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "file_kind"]),
            models.Index(fields=["website", "lifecycle_status"]),
            models.Index(fields=["website", "scan_status"]),
            models.Index(fields=["site", "lifecycle_status"]),
            models.Index(fields=["site", "bucket", "lifecycle_status"]),
            models.Index(fields=["sha256_hash"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["delete_after"]),
        ]

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.uuid})"

    @property
    def public_url(self) -> str | None:
        """Return the CDN URL for public files when available."""
        if not self.is_public:
            return None
        if self.bucket.is_public and self.bucket.cdn_endpoint:
            return f"{self.bucket.cdn_endpoint.rstrip('/')}/{self.storage_key}"
        return None
