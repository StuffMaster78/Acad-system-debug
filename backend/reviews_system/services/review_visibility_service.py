from reviews_system.models import Review
from reviews_system.models.states import (
    ReviewVisibility,
)


class ReviewVisibilityService:
    """Handles review visibility changes."""

    @classmethod
    def set_public(
        cls,
        *,
        review: Review,
    ) -> Review:
        """Mark review as public."""
        review.visibility = ReviewVisibility.PUBLIC
        review.save(update_fields=["visibility"])

        return review

    @classmethod
    def set_shadowed(
        cls,
        *,
        review: Review,
    ) -> Review:
        """Shadow a review."""
        review.visibility = ReviewVisibility.SHADOWED
        review.save(update_fields=["visibility"])

        return review

    @classmethod
    def set_removed(
        cls,
        *,
        review: Review,
    ) -> Review:
        """Remove review visibility."""
        review.visibility = ReviewVisibility.REMOVED
        review.save(update_fields=["visibility"])

        return review