from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ValidationError

from reviews_system.models import Review
from shared.enums.review_targets import ReviewTarget


class ReviewValidationService:
    """Handles review validation rules."""

    @classmethod
    def validate_rating(
        cls,
        rating: Decimal,
    ) -> None:
        """Validate rating range."""
        if rating < Decimal("0"):
            raise ValidationError(
                "Rating cannot be below 0."
            )

        if rating > Decimal("5"):
            raise ValidationError(
                "Rating cannot exceed 5."
            )

    @classmethod
    def validate_target_type(
        cls,
        target_type: str,
    ) -> None:
        """Validate review target type."""
        valid_targets = ReviewTarget.values

        if target_type not in valid_targets:
            raise ValidationError(
                "Invalid review target type."
            )

    @classmethod
    def validate_duplicate_review(
        cls,
        reviewer_id: UUID,
        target_type: str,
        target_id: UUID,
    ) -> None:
        """Prevent duplicate reviews."""
        exists = Review.objects.filter(
            reviewer_id=reviewer_id,
            target_type=target_type,
            target_id=target_id,
        ).exists()

        if exists:
            raise ValidationError(
                "Review already exists."
            )