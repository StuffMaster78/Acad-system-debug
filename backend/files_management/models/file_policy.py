from django.db import models

from files_management.constants import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_FILE_MIME_TYPES,
    DEFAULT_MAX_FILE_SIZE_BYTES,
)
from files_management.enums import FilePurpose


class FilePolicy(models.Model):
    """
    Defines tenant configurable file rules.

    File policies allow each website to control accepted file types,
    size limits, external link behavior, and review requirements by
    purpose. This keeps platform defaults safe while giving admins
    enough flexibility to support real academic workflows.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_policies",
    )

    name = models.CharField(
        max_length=150,
        help_text="Human readable policy name.",
    )

    purpose = models.CharField(
        max_length=64,
        choices=FilePurpose.choices,
        help_text="Attachment purpose this policy applies to.",
    )

    allowed_mime_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Allowed MIME types. Empty falls back to defaults.",
    )

    allowed_extensions = models.JSONField(
        default=list,
        blank=True,
        help_text="Allowed extensions. Empty falls back to defaults.",
    )

    max_file_size_bytes = models.PositiveBigIntegerField(
        default=DEFAULT_MAX_FILE_SIZE_BYTES,
    )

    allow_external_links = models.BooleanField(
        default=False,
    )

    external_links_require_review = models.BooleanField(
        default=True,
    )

    allowed_external_providers = models.JSONField(
        default=list,
        blank=True,
    )

    require_scan_before_download = models.BooleanField(
        default=False,
    )

    require_review_before_download = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "purpose")
        ordering = ["purpose"]
        indexes = [
            models.Index(fields=["website", "purpose"]),
            models.Index(fields=["is_active"]),
        ]

    def get_allowed_mime_types(self) -> list[str]:
        """
        Return configured MIME types or platform defaults.
        """

        if self.allowed_mime_types:
            return list(self.allowed_mime_types)

        return list(ALLOWED_FILE_MIME_TYPES)

    def get_allowed_extensions(self) -> list[str]:
        """
        Return configured extensions or platform defaults.
        """

        if self.allowed_extensions:
            return list(self.allowed_extensions)

        return list(ALLOWED_FILE_EXTENSIONS)

    def __str__(self) -> str:
        return f"{self.website.pk}: {self.purpose}"