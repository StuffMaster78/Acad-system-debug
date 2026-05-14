from django.db.models import QuerySet

from reviews_system.models.review import Review
from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)


class ReviewSelectors:
    """Query layer for reviews."""

    @staticmethod
    def base_queryset() -> QuerySet[Review]:
        """Base queryset for all review queries."""
        return Review.objects.all()

    @staticmethod
    def public_reviews() -> QuerySet[Review]:
        """Return publicly visible reviews."""
        return ReviewSelectors.base_queryset().filter(
            moderation_state=ReviewState.APPROVED,
            visibility=ReviewVisibility.PUBLIC,
        )

    @staticmethod
    def writer_reviews(
        *,
        writer_id: str,
    ) -> QuerySet[Review]:
        """Return public reviews for a writer."""
        return ReviewSelectors.public_reviews().filter(
            writer_id=writer_id,
        )

    @staticmethod
    def target_reviews(
        *,
        target_type: str,
        target_id: str,
    ) -> QuerySet[Review]:
        """Return public reviews for a target."""
        return ReviewSelectors.public_reviews().filter(
            target_type=target_type,
            target_id=target_id,
        )

    @staticmethod
    def all_reviews() -> QuerySet[Review]:
        """Return all reviews (admin/internal use)."""
        return ReviewSelectors.base_queryset()