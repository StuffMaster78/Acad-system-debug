from event_system.contracts.domain_event import DomainEvent
from event_system.contracts.event_types import EventTypes


class EventFactory:
    """
    Single responsibility:
    Convert domain actions → DomainEvent.
    """

    @staticmethod
    def review_approved(
        *,
        review_id: str,
        target_type: str,
        target_id: str,
        actor_id: str | None,
    ) -> DomainEvent:

        return DomainEvent(
            event_type=EventTypes.REVIEW_APPROVED,
            aggregate_id=str(review_id),
            aggregate_type="review",
            actor_id=str(actor_id) if actor_id else None,
            payload={
                "target_type": target_type,
                "target_id": str(target_id),
            },
        )

    @staticmethod
    def bonus_performance(
        *,
        writer_id: str,
        order_id: str,
        amount: str,
    ) -> DomainEvent:

        return DomainEvent(
            event_type=EventTypes.BONUS_PERFORMANCE,
            aggregate_id=str(order_id),
            aggregate_type="bonus",
            actor_id=str(writer_id),
            payload={
                "writer_id": str(writer_id),
                "order_id": str(order_id),
                "amount": amount,
            },
        )