import uuid

from django.db import models

from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)


class ReviewModerationLog(models.Model):
    """Tracks moderation changes for reviews."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    review_id = models.UUIDField(
        db_index=True,
    )

    previous_state = models.CharField(
        max_length=30,
        choices=ReviewState.choices,
    )

    new_state = models.CharField(
        max_length=30,
        choices=ReviewState.choices,
    )

    previous_visibility = models.CharField(
        max_length=30,
        choices=ReviewVisibility.choices,
    )

    new_visibility = models.CharField(
        max_length=30,
        choices=ReviewVisibility.choices,
    )

    reason = models.TextField(
        blank=True,
    )

    moderator_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return readable moderation log."""
        return (
            f"ModerationLog("
            f"review_id={self.review_id})"
        )