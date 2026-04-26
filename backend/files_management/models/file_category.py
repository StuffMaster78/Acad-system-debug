from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "code")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"