from uuid import UUID

from reviews_system.models import Review
from reviews_system.services.review_moderation_service import (
    ReviewModerationService,
)


def _to_uuid(value: str | None) -> UUID | None:
    if value is None:
        return None
    return UUID(value)


def approve_review_task(
    review_id: str,
    moderator_id: str | None = None,
    reason: str = "",
) -> None:
    review = Review.objects.get(id=review_id)

    ReviewModerationService.approve(
        review=review,
        moderator_id=_to_uuid(moderator_id),
        reason=reason,
    )


def reject_review_task(
    review_id: str,
    moderator_id: str | None = None,
    reason: str = "",
) -> None:
    review = Review.objects.get(id=review_id)

    ReviewModerationService.reject(
        review=review,
        moderator_id=_to_uuid(moderator_id),
        reason=reason,
    )


def shadow_review_task(
    review_id: str,
    moderator_id: str | None = None,
    reason: str = "",
) -> None:
    review = Review.objects.get(id=review_id)

    ReviewModerationService.shadow(
        review=review,
        moderator_id=_to_uuid(moderator_id),
        reason=reason,
    )


def flag_review_task(
    review_id: str,
    moderator_id: str | None = None,
    reason: str = "",
) -> None:
    review = Review.objects.get(id=review_id)

    ReviewModerationService.flag(
        review=review,
        moderator_id=_to_uuid(moderator_id),
        reason=reason,
    )