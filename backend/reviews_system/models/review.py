import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)
from shared.enums.review_targets import ReviewTarget


class Review(models.Model):
    """
    Unified review model.

    Supports:
        • orders
        • special orders
        • class orders
        • websites
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    reviewer_id = models.UUIDField(db_index=True)

    target_type = models.CharField(
        max_length=40,
        choices=ReviewTarget.choices,
        db_index=True,
    )

    target_id = models.UUIDField(db_index=True)

    writer_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
    )

    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    rating_payload = models.JSONField(default=dict, blank=True)

    moderation_state = models.CharField(
        max_length=30,
        choices=ReviewState.choices,
        default=ReviewState.PENDING,
        db_index=True,
    )

    visibility = models.CharField(
        max_length=30,
        choices=ReviewVisibility.choices,
        default=ReviewVisibility.UNDER_REVIEW,
        db_index=True,
    )

    is_verified = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)

    flag_reason = models.TextField(blank=True, null=True)

    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True)
    moderated_by_id = models.UUIDField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["writer_id", "visibility"]),
            models.Index(fields=["target_type", "visibility"]),
        ]

    def clean(self) -> None:
        super().clean()

        if self.rating < Decimal("0"):
            raise ValidationError({"rating": "Rating cannot be below 0."})

        if self.rating > Decimal("5"):
            raise ValidationError({"rating": "Rating cannot exceed 5."})

        if (
            self.target_type == ReviewTarget.WEBSITE
            and self.writer_id is not None
        ):
            raise ValidationError(
                {"writer_id": "Website reviews cannot have writer_id."}
            )

    def __str__(self) -> str:
        return f"{self.target_type} review ({self.rating})"