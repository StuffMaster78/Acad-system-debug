from uuid import UUID

from reviews_system.events.review_event_types import ReviewEventType


class ReviewEvent:
    """
    Domain event structure for reviews.
    """

    def __init__(
        self,
        event_type: str,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
        payload: dict,
    ) -> None:
        self.event_type = event_type
        self.review_id = review_id
        self.target_type = target_type
        self.target_id = target_id
        self.actor_id = actor_id
        self.payload = payload


class ReviewEventBuilder:
    """
    Builds domain events from review actions.
    """

    @staticmethod
    def build_created(
        *,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
    ) -> ReviewEvent:
        return ReviewEvent(
            event_type=ReviewEventType.CREATED,
            review_id=review_id,
            target_type=target_type,
            target_id=target_id,
            actor_id=actor_id,
            payload={},
        )

    @staticmethod
    def build_approved(
        *,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
    ) -> ReviewEvent:
        return ReviewEvent(
            event_type=ReviewEventType.APPROVED,
            review_id=review_id,
            target_type=target_type,
            target_id=target_id,
            actor_id=actor_id,
            payload={},
        )

    @staticmethod
    def build_shadowed(
        *,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
    ) -> ReviewEvent:
        return ReviewEvent(
            event_type=ReviewEventType.SHADOWED,
            review_id=review_id,
            target_type=target_type,
            target_id=target_id,
            actor_id=actor_id,
            payload={},
        )

    @staticmethod
    def build_rejected(
        *,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
    ) -> ReviewEvent:
        """Build review rejected event."""
        return ReviewEvent(
            event_type=ReviewEventType.REJECTED,
            review_id=review_id,
            target_type=target_type,
            target_id=target_id,
            actor_id=actor_id,
            payload={},
        )

    @staticmethod
    def build_flagged(
        *,
        review_id: UUID,
        target_type: str,
        target_id: UUID,
        actor_id: UUID | None,
    ) -> ReviewEvent:
        """Build review flagged event."""
        return ReviewEvent(
            event_type=ReviewEventType.FLAGGED,
            review_id=review_id,
            target_type=target_type,
            target_id=target_id,
            actor_id=actor_id,
            payload={},
        )