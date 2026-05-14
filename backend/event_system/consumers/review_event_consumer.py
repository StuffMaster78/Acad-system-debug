from event_system.models.event_outbox import EventOutbox
from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)


class ReviewEventConsumer:
    """
    Pure event handlers.
    """

    @staticmethod
    def handle_approved(event: EventOutbox) -> None:
        payload = event.payload

        ReputationAggregationService.process_review_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
            actor_id=payload.get("actor_id"),
        )

    @staticmethod
    def handle_shadowed(event: EventOutbox) -> None:
        payload = event.payload

        ReputationAggregationService.process_shadow_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
        )

    @staticmethod
    def handle_rejected(event: EventOutbox) -> None:
        payload = event.payload

        ReputationAggregationService.process_rejection_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
        )


ROUTES = {
    "review.approved": ReviewEventConsumer.handle_approved,
    "review.shadowed": ReviewEventConsumer.handle_shadowed,
    "review.rejected": ReviewEventConsumer.handle_rejected,
}