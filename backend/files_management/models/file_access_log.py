"""
FileAccessLog — audit trail of every file access event.
"""

from django.conf import settings
from django.db import models

from files_management.enums import FileAccessType


class FileAccessLog(models.Model):
    """
    Audit trail for file operations.

    Every view, download, upload, delete, scan, and derivative
    generation is recorded. Used for security audits, usage analytics,
    and abuse detection.
    """

    file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.CASCADE,
        related_name="access_logs",
    )

    access_type = models.CharField(
        max_length=20,
        choices=FileAccessType.choices,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    bytes_transferred = models.BigIntegerField(default=0)

    success = models.BooleanField(default=True)
    error_detail = models.TextField(blank=True)

    # Extra context
    request_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional request context (headers, referrer, etc.)",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["file", "created_at"]),
            models.Index(fields=["access_type", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_access_type_display()} — {self.file.original_filename}"
