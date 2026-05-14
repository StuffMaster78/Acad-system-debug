import uuid

from event_system.models.event_outbox import EventOutbox
from reviews_system.events.review_event_builder import ReviewEvent


class EventBusService:
    """
    Converts domain events into durable outbox events.

    This is the ONLY entry point for event persistence.
    """

    @classmethod
    def publish(cls, event: ReviewEvent) -> EventOutbox:
        """
        Store event in outbox table for async processing.
        """

        payload = {
            "review_id": str(event.review_id),
            "target_type": event.target_type,
            "target_id": str(event.target_id),
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "payload": event.payload,
        }

        outbox_event = EventOutbox.objects.create(
            event_type=event.event_type,
            domain="reviews",
            payload=payload,
            routing_key=cls._build_routing_key(event),
            idempotency_key=cls._build_idempotency_key(event),
            status="pending",
            attempts=0,
        )

        return outbox_event

    @staticmethod
    def _build_routing_key(event: ReviewEvent) -> str:
        return f"reviews.{event.event_type}.v1"

    @staticmethod
    def _build_idempotency_key(event: ReviewEvent) -> str:
        return f"{event.event_type}:{event.review_id}"