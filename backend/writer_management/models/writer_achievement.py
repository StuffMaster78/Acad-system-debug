# writer_management/models/writer_achievement.py

from __future__ import annotations

from django.db import models
from django.utils import timezone

from websites.models.websites import Website
from writer_management.models.writer_profile import (
    WriterProfile,
)


class WriterAchievement(
    models.Model,
):
    """
    Immutable writer achievement record.

    Represents milestone, excellence,
    trust, or specialization accomplishments.
    """

    class AchievementType(
        models.TextChoices,
    ):
        QUALITY = (
            "QUALITY",
            "Quality",
        )
        SPEED = (
            "SPEED",
            "Speed",
        )
        TRUST = (
            "TRUST",
            "Trust",
        )
        SPECIALIZATION = (
            "SPECIALIZATION",
            "Specialization",
        )
        CONSISTENCY = (
            "CONSISTENCY",
            "Consistency",
        )
        MILESTONE = (
            "MILESTONE",
            "Milestone",
        )

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

    achievement_type = models.CharField(
        max_length=40,
        choices=AchievementType.choices,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=120,
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    badge_name = models.CharField(
        max_length=120,
        blank=True,
    )

    icon = models.CharField(
        max_length=120,
        blank=True,
    )

    points = models.PositiveIntegerField(
        default=0,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    earned_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = [
            "-earned_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "website",
                    "writer",
                ],
                name="writer_achievement_idx",
            ),
            models.Index(
                fields=[
                    "achievement_type",
                ],
                name="achievement_type_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "writer",
                    "slug",
                ],
                name="unique_writer_achievement_slug",
            ),
        ]

    def __str__(
        self,
    ) -> str:
        return (
            f"{self.writer.registration_id} | "
            f"{self.title}"
        )