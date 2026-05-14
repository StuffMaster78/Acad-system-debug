from event_system.models.event_outbox import EventOutbox
from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)


class ReputationEventConsumer:
    """
    Consumes domain events and updates reputation state.
    """

    @staticmethod
    def handle(event: EventOutbox) -> None:
        """
        Route events to reputation logic.
        """

        if event.event_type == "review.approved":
            ReputationEventConsumer._on_review_approved(event)

        elif event.event_type == "review.shadowed":
            ReputationEventConsumer._on_review_shadowed(event)

        elif event.event_type == "review.rejected":
            ReputationEventConsumer._on_review_rejected(event)

    @staticmethod
    def _on_review_approved(event: EventOutbox) -> None:
        """
        Approved reviews directly impact reputation.
        """

        payload = event.payload

        ReputationAggregationService.process_review_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
            actor_id=payload.get("actor_id"),
        )

    @staticmethod
    def _on_review_shadowed(event: EventOutbox) -> None:
        """
        Shadowed reviews must be excluded or downgraded.
        """

        payload = event.payload

        ReputationAggregationService.process_shadow_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
        )

    @staticmethod
    def _on_review_rejected(event: EventOutbox) -> None:
        """
        Rejected reviews should be removed from calculations.
        """

        payload = event.payload

        ReputationAggregationService.process_rejection_event(
            review_id=payload["review_id"],
            target_type=payload["target_type"],
            target_id=payload["target_id"],
        )