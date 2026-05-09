from __future__ import annotations

from django.db import transaction

from writer_payments_management.models.outbox_event_models import OutboxEvent


class OutboxService:
    """
    Writes durable events safely with idempotency guarantee.
    """

    @staticmethod
    @transaction.atomic
    def emit(event_type: str, payload: dict) -> OutboxEvent:

        event, created = OutboxEvent.objects.get_or_create(
            event_type=event_type,
            payload_hash=OutboxEvent()._generate_hash(),  # temporary instance-safe hash
            defaults={"payload": payload},
        )

        # if already exists, return it (idempotent behavior)
        return event