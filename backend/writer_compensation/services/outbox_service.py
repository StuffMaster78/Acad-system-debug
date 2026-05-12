from __future__ import annotations
 
import hashlib
import json
 
from django.db import transaction
 
from writer_compensation.models.outbox_event_models import OutboxEvent
 

def _hash_payload(payload: dict) -> str:
    """
    Compute the same hash OutboxEvent._generate_hash() uses.
    """
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()
 
 
class OutboxService:
    """
    Writes durable events safely with idempotency guarantee.
 
    Each (event_type, payload_hash) pair is unique — calling emit()
    twice with the same arguments returns the existing record without
    creating a duplicate. This makes it safe for retry loops and
    transactional outbox patterns.
    """
 
    @staticmethod
    @transaction.atomic
    def emit(event_type: str, payload: dict) -> OutboxEvent:
        """
        Emit a durable event into the outbox.
 
        Idempotent: identical (event_type, payload) combinations return
        the existing OutboxEvent without creating a duplicate.
 
        Returns the OutboxEvent (created or existing).
        """
        # FIX: compute hash from the actual payload, not an empty instance.
        payload_hash = _hash_payload(payload)
 
        event, _ = OutboxEvent.objects.get_or_create(
            event_type=event_type,
            payload_hash=payload_hash,
            defaults={"payload": payload},
        )
 
        return event