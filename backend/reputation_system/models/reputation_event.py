from django.db import models
from django.utils import timezone


class ReputationEvent(models.Model):
    """
    Persistent log of all reputation changes.

    This is NOT business logic.
    This is:
        - audit trail
        - debugging tool
        - replay source (future upgrade)
    """

    class EventType(models.TextChoices):
        REVIEW_PROCESSED = "review.processed"
        REVIEW_SHADOWED = "review.shadowed"
        REVIEW_REJECTED = "review.rejected"
        REPUTATION_RECALCULATED = "reputation.recalculated"

    id = models.UUIDField(
        primary_key=True,
        editable=False,
    )

    event_type = models.CharField(
        max_length=64,
        choices=EventType.choices,
        db_index=True,
    )

    target_type = models.CharField(
        max_length=32,
        db_index=True,
    )

    target_id = models.UUIDField(
        db_index=True,
    )

    review_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    actor_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    payload = models.JSONField(
        default=dict,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["target_type", "target_id"],
            ),
            models.Index(
                fields=["event_type", "created_at"],
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.target_type}:{self.target_id}"