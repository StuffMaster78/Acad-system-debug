from uuid import UUID

from django.db import transaction
from django.utils import timezone

from reviews_system.events.review_event_builder import (
    ReviewEventBuilder,
)
from reviews_system.models import (
    Review,
    ReviewModerationLog,
)
from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)
from reviews_system.services.review_visibility_service import (
    ReviewVisibilityService,
)


class ReviewModerationService:
    """
    Handles review moderation lifecycle.

    Responsibilities:
        - state transitions
        - visibility delegation
        - audit logging
        - event emission
    """

    @classmethod
    @transaction.atomic
    def approve(
        cls,
        *,
        review: Review,
        moderator_id: UUID | None = None,
        reason: str = "",
    ) -> Review:
        """Approve review and publish it."""

        previous_state = review.moderation_state
        previous_visibility = review.visibility

        cls._apply_moderation_base(
            review=review,
            state=ReviewState.APPROVED,
            moderator_id=moderator_id,
            reason=reason,
        )

        ReviewVisibilityService.set_public(review=review)

        cls._log(
            review=review,
            moderator_id=moderator_id,
            previous_state=previous_state,
            new_state=ReviewState.APPROVED,
            previous_visibility=previous_visibility,
            new_visibility=ReviewVisibility.PUBLIC,
            reason=reason,
        )

        cls._emit(
            ReviewEventBuilder.build_approved(
                review_id=review.id,
                target_type=review.target_type,
                target_id=review.target_id,
                actor_id=moderator_id,
            )
        )

        return review

    @classmethod
    @transaction.atomic
    def reject(
        cls,
        *,
        review: Review,
        moderator_id: UUID | None = None,
        reason: str = "",
    ) -> Review:
        """Reject review."""

        previous_state = review.moderation_state
        previous_visibility = review.visibility

        cls._apply_moderation_base(
            review=review,
            state=ReviewState.REJECTED,
            moderator_id=moderator_id,
            reason=reason,
        )

        ReviewVisibilityService.set_removed(review=review)

        cls._log(
            review=review,
            moderator_id=moderator_id,
            previous_state=previous_state,
            new_state=ReviewState.REJECTED,
            previous_visibility=previous_visibility,
            new_visibility=ReviewVisibility.REMOVED,
            reason=reason,
        )

        cls._emit(
            ReviewEventBuilder.build_rejected(
                review_id=review.id,
                target_type=review.target_type,
                target_id=review.target_id,
                actor_id=moderator_id,
            )
        )

        return review

    @classmethod
    @transaction.atomic
    def shadow(
        cls,
        *,
        review: Review,
        moderator_id: UUID | None = None,
        reason: str = "",
    ) -> Review:
        """Shadow review from public view."""

        previous_state = review.moderation_state
        previous_visibility = review.visibility

        cls._apply_moderation_base(
            review=review,
            state=ReviewState.APPROVED,
            moderator_id=moderator_id,
            reason=reason,
        )

        ReviewVisibilityService.set_shadowed(review=review)

        cls._log(
            review=review,
            moderator_id=moderator_id,
            previous_state=previous_state,
            new_state=ReviewState.APPROVED,
            previous_visibility=previous_visibility,
            new_visibility=ReviewVisibility.SHADOWED,
            reason=reason,
        )

        cls._emit(
            ReviewEventBuilder.build_shadowed(
                review_id=review.id,
                target_type=review.target_type,
                target_id=review.target_id,
                actor_id=moderator_id,
            )
        )

        return review

    @classmethod
    @transaction.atomic
    def flag(
        cls,
        *,
        review: Review,
        moderator_id: UUID | None = None,
        reason: str = "",
    ) -> Review:
        """Flag review for investigation."""

        previous_state = review.moderation_state
        previous_visibility = review.visibility

        cls._apply_moderation_base(
            review=review,
            state=ReviewState.FLAGGED,
            moderator_id=moderator_id,
            reason=reason,
        )

        cls._log(
            review=review,
            moderator_id=moderator_id,
            previous_state=previous_state,
            new_state=ReviewState.FLAGGED,
            previous_visibility=previous_visibility,
            new_visibility=previous_visibility,
            reason=reason,
        )

        cls._emit(
            ReviewEventBuilder.build_flagged(
                review_id=review.id,
                target_type=review.target_type,
                target_id=review.target_id,
                actor_id=moderator_id,
            )
        )

        return review

    @classmethod
    def _apply_moderation_base(
        cls,
        *,
        review: Review,
        state: ReviewState,
        moderator_id: UUID | None,
        reason: str,
    ) -> None:
        """Centralized state mutation logic."""

        review.moderation_state = state
        review.moderated_at = timezone.now()
        review.moderated_by_id = moderator_id
        review.moderation_notes = reason

        review.save(
            update_fields=[
                "moderation_state",
                "moderated_at",
                "moderated_by_id",
                "moderation_notes",
            ]
        )

    @classmethod
    def _log(
        cls,
        *,
        review: Review,
        moderator_id: UUID | None,
        previous_state: str,
        new_state: str,
        previous_visibility: str,
        new_visibility: str,
        reason: str,
    ) -> None:
        """Write moderation audit log."""

        ReviewModerationLog.objects.create(
            review_id=review.id,
            moderator_id=moderator_id,
            previous_state=previous_state,
            new_state=new_state,
            previous_visibility=previous_visibility,
            new_visibility=new_visibility,
            reason=reason,
        )

    @classmethod
    def _emit(cls, event) -> None:
        """Emit domain event."""

        from event_system.services.event_bus_service import (
            EventBusService,
        )

        EventBusService.publish(event)