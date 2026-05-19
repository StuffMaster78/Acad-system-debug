"""
Admin-managed resources for writer development.
No writer-specific identity — resources are site-level content.

WriterResourceCategory  — organises resources
WriterResource          — the resource itself (doc, link, video, article)
WriterResourceView      — tracks which writers viewed which resources
"""

from django.conf import settings
from django.db import models


class WriterResourceCategory(models.Model):
    """Category for grouping writer resources."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_resource_categories",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Resource Category"
        verbose_name_plural = "Writer Resource Categories"
        ordering = ["display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_resource_category_per_site",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class WriterResource(models.Model):
    """
    A resource available to writers for professional development.

    Types: document, link, video, article, tool.
    view_count and download_count are cached counters —
    incremented by resource_service, never set directly.
    """

    class ResourceType(models.TextChoices):
        DOCUMENT = "document", "Document (PDF, DOC, etc.)"
        LINK     = "link",     "External Link"
        VIDEO    = "video",    "Video"
        ARTICLE  = "article",  "Article / Guide"
        TOOL     = "tool",     "Tool / Software"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_resources",
    )
    category = models.ForeignKey(
        WriterResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.DOCUMENT,
    )
    # file = models.FileField(
    #     upload_to="writer_resources/",
    #     null=True,
    #     blank=True,
    # )
    file_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL returned by the files management app after upload.",
    )
    files_app_file_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="PK of the file in the files_management app.",
    )
    external_url = models.URLField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    content = models.TextField(
        blank=True,
        default="",
        help_text="Rich text content for article type resources.",
    )
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_writer_resources",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_writer_resources",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Resource"
        verbose_name_plural = "Writer Resources"
        ordering = ["display_order", "-created_at"]
        indexes = [
            models.Index(
                fields=["website", "is_active", "is_featured"],
                name="writer_res_active_feat_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.resource_type}]"


class WriterResourceView(models.Model):
    """
    Records that a specific writer viewed a specific resource.

    Used for analytics and to show writers which resources
    they have already seen.

    UniqueConstraint ensures one record per writer per resource —
    subsequent views update viewed_at rather than creating new rows.
    """

    resource = models.ForeignKey(
        WriterResource,
        on_delete=models.CASCADE,
        related_name="views",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="resource_views",
    )
    viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(
        default=1,
        help_text="How many times this writer viewed this resource.",
    )

    class Meta:
        verbose_name = "Writer Resource View"
        verbose_name_plural = "Writer Resource Views"
        constraints = [
            models.UniqueConstraint(
                fields=["resource", "writer"],
                name="unique_resource_view_per_writer",
            ),
        ]
        indexes = [
            models.Index(
                fields=["writer", "viewed_at"],
                name="resource_view_writer_time_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterResourceView writer={self.writer.pk} "
            f"resource={self.resource.pk}"
        )
