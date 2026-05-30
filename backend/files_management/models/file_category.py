from django.db import models

from files_management.enums import FileVisibility


class FileCategory(models.Model):
    """
    Represents a reusable classification for files.

    Categories allow grouping files by business meaning such as
    "final paper", "avatar", "CMS image", or "verification document".

    This is tenant-aware to allow different websites to define their
    own file structures and semantics.
    """

    name = models.CharField(
        max_length=120,
        help_text="Human-readable name for the category.",
    )

    code = models.CharField(
        max_length=120,
        help_text="Stable internal identifier for the category.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the category.",
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_categories",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the category is currently in use.",
    )

    # ------------------------------------------------------------------
    # Per-category upload policy
    # ------------------------------------------------------------------

    default_visibility = models.CharField(
        max_length=64,
        choices=FileVisibility.choices,
        default=FileVisibility.PRIVATE,
        help_text=(
            "Default visibility applied to attachments in this category "
            "when no visibility is explicitly set by the uploader."
        ),
    )

    max_file_size_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Maximum upload size for this category in bytes. "
            "Overrides the FilePolicy limit when set."
        ),
    )

    require_scan_before_download = models.BooleanField(
        default=True,
        help_text=(
            "Block downloads until the file scan has passed. "
            "Disable only for categories where scan latency is unacceptable."
        ),
    )

    require_approval_before_download = models.BooleanField(
        default=False,
        help_text=(
            "Require explicit staff approval before files in this category "
            "become downloadable. Useful for screenshots and grade evidence."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "code")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"