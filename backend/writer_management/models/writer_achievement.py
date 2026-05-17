from __future__ import annotations

from django.db import models

from websites.models.websites import Website
from writer_management.models.writer_profile import (
    WriterProfile,
)


class WriterAchievement(models.Model):
    """
    Immutable writer achievement record.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_achievements",
    )

    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="achievements",
    )

    slug = models.SlugField(
        max_length=120,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    badge = models.CharField(
        max_length=120,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    awarded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-awarded_at"]

        indexes = [
            models.Index(
                fields=["writer", "slug"],
                name="writer_achievement_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "writer",
                    "slug",
                ],
                name=(
                    "unique_writer_achievement"
                ),
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.writer.registration_id} "
            f"| {self.title}"
        )