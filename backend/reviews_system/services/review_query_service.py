from django.db.models import QuerySet

from reviews_system.models import Review
from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)
from shared.enums.review_targets import ReviewTarget


class ReviewQueryService:
    """
    Centralized read layer for reviews.

    This ensures:
        - consistent filtering rules
        - no direct ORM scattering in views
        - safe reputation ingestion queries
    """

    @classmethod
    def public_reviews(cls) -> QuerySet[Review]:
        """
        Return reviews visible to end users.
        """

        return Review.objects.filter(
            moderation_state=ReviewState.APPROVED,
            visibility=ReviewVisibility.PUBLIC,
        )

    @classmethod
    def shadowed_reviews(cls) -> QuerySet[Review]:
        """
        Return shadowed reviews (internal only).
        """

        return Review.objects.filter(
            visibility=ReviewVisibility.SHADOWED,
        )

    @classmethod
    def flagged_reviews(cls) -> QuerySet[Review]:
        """
        Return reviews flagged for moderation review.
        """

        return Review.objects.filter(
            moderation_state=ReviewState.FLAGGED,
        )

    @classmethod
    def pending_reviews(cls) -> QuerySet[Review]:
        """
        Return reviews waiting for moderation.
        """

        return Review.objects.filter(
            moderation_state=ReviewState.PENDING,
        )

    @classmethod
    def by_target(
        cls,
        *,
        target_type: str,
        target_id: str,
    ) -> QuerySet[Review]:
        """
        Return all public reviews for a target entity.
        """

        return cls.public_reviews().filter(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def by_writer(
        cls,
        *,
        writer_id: str,
    ) -> QuerySet[Review]:
        """
        Return all public reviews for a writer.
        """

        return cls.public_reviews().filter(
            writer_id=writer_id,
        )

    @classmethod
    def website_reviews(cls) -> QuerySet[Review]:
        """
        Return all website reviews (public only).
        """

        return cls.public_reviews().filter(
            target_type=ReviewTarget.WEBSITE,
        )

    @classmethod
    def reputation_eligible_reviews(cls) -> QuerySet[Review]:
        """
        Return reviews eligible for reputation scoring.

        Strict rule:
            Only APPROVED + PUBLIC reviews count.
        """

        return Review.objects.filter(
            moderation_state=ReviewState.APPROVED,
            visibility=ReviewVisibility.PUBLIC,
        )

    @classmethod
    def moderation_queue(cls) -> QuerySet[Review]:
        """
        Return reviews requiring moderator attention.
        """

        return Review.objects.filter(
            moderation_state__in=[
                ReviewState.PENDING,
                ReviewState.FLAGGED,
            ],
        )