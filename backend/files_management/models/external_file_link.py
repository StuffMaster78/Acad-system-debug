from django.conf import settings
from django.db import models

from files_management.enums import (
    ExternalFileProvider,
    ExternalFileReviewStatus,
)


class ExternalFileLink(models.Model):
    """
    Represents a remotely hosted file or folder.

    External links are useful for large files, Google Docs, Google
    Slides, Google Sheets, Dropbox folders, Loom videos, and other
    content that is not uploaded directly into platform storage.

    External links are intentionally reviewed before normal users can
    rely on them. This protects clients, writers, and staff from broken
    links, phishing links, unsafe files, and accidental data exposure.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="external_file_links",
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_external_file_links",
    )

    provider = models.CharField(
        max_length=40,
        choices=ExternalFileProvider.choices,
        default=ExternalFileProvider.OTHER,
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional readable label for the external file.",
    )

    url = models.URLField(
        max_length=1000,
        help_text="External file or folder URL.",
    )

    review_status = models.CharField(
        max_length=32,
        choices=ExternalFileReviewStatus.choices,
        default=ExternalFileReviewStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_external_file_links",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    review_note = models.TextField(
        blank=True,
        help_text="Staff note explaining approval or rejection.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Inactive links are hidden from normal workflows.",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider metadata, permissions, or extracted info.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "review_status"]),
            models.Index(fields=["provider"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        label = self.title or self.url
        return f"{label} [{self.review_status}]"