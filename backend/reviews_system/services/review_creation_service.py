from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import transaction

from reviews_system.models import Review
from reviews_system.services.review_validation_service import (
    ReviewValidationService,
)


class ReviewCreationService:
    """Handles review creation workflow."""

    @classmethod
    @transaction.atomic
    def create_review(
        cls,
        *,
        reviewer_id: UUID,
        target_type: str,
        target_id: UUID,
        rating: Decimal,
        comment: str = "",
        title: str = "",
        writer_id: UUID | None = None,
        rating_payload: dict[str, Any] | None = None,
    ) -> Review:
        """Create a validated review."""

        ReviewValidationService.validate_rating(
            rating=rating,
        )

        ReviewValidationService.validate_target_type(
            target_type=target_type,
        )

        ReviewValidationService.validate_duplicate_review(
            reviewer_id=reviewer_id,
            target_type=target_type,
            target_id=target_id,
        )

        review = Review.objects.create(
            reviewer_id=reviewer_id,
            target_type=target_type,
            target_id=target_id,
            writer_id=writer_id,
            rating=rating,
            title=title,
            comment=comment,
            rating_payload=rating_payload or {},
        )

        return review