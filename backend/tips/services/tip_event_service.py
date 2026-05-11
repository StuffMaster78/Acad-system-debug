from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction

from tips.models.tip_outbox_event import TipOutboxEvent


class TipEventService:
    """
    Canonical outbox event emitter.

    Guarantees:
        - deduplicated events
        - transactional durability
        - replay protection
        - consistent payload structure
    """

    @staticmethod
    def _build_deduplication_key(
        *,
        tip_id: Any,
        event_type: str,
        payload: dict[str, Any],
    ) -> str:

        serialized_payload = json.dumps(
            payload,
            sort_keys=True,
            default=str,
        )

        raw = (
            f"{tip_id}:"
            f"{event_type}:"
            f"{serialized_payload}"
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    @staticmethod
    @transaction.atomic
    def emit(
        *,
        tip,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> TipOutboxEvent:

        payload = payload or {}

        deduplication_key = (
            TipEventService._build_deduplication_key(
                tip_id=tip.pk,
                event_type=event_type,
                payload=payload,
            )
        )

        event, _ = TipOutboxEvent.objects.get_or_create(
            deduplication_key=deduplication_key,
            defaults={
                "tip": tip,
                "event_type": event_type,
                "payload": payload,
            },
        )

        return event