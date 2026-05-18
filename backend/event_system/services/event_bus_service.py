from __future__ import annotations

from django.db import transaction

from event_system.events.base_event import (
    BaseDomainEvent,
)
from event_system.models.event_outbox import (
    EventOutbox,
)
from event_system.services.post_commit_event_hooks import (
    on_commit_publish,
)


class EventBusService:
    """
    Durable event persistence layer.

    Converts domain events into outbox events.
    """

    @classmethod
    def publish(
        cls,
        event: BaseDomainEvent,
    ) -> EventOutbox:
        """
        Persist domain event.
        """

        outbox_event = (
            EventOutbox.objects.create(
                event_type=event.event_type,
                domain=event.domain,
                payload=event.payload,
                routing_key=cls._build_routing_key(
                    event=event,
                ),
                idempotency_key=(
                    cls._build_idempotency_key(
                        event=event,
                    )
                ),
                status="pending",
                attempts=0,
            )
        )

        transaction.on_commit(
            lambda event_id=str(
                outbox_event.id,
            ): on_commit_publish(
                event_id,
            )
        )

        return outbox_event

    @staticmethod
    def _build_routing_key(
        *,
        event: BaseDomainEvent,
    ) -> str:
        return (
            f"{event.domain}."
            f"{event.event_type}.v1"
        )

    @staticmethod
    def _build_idempotency_key(
        *,
        event: BaseDomainEvent,
    ) -> str:
        return (
            f"{event.domain}:"
            f"{event.event_type}:"
            f"{event.aggregate_id}"
        )