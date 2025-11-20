# notifications_system/services/outbox.py
from __future__ import annotations
from typing import Optional
from django.db import transaction
from django.utils import timezone
from notifications_system.models.outbox import Outbox

def enqueue_outbox(
    event_key: str,
    payload: dict,
    website_id: Optional[int] = None,
    user_id: Optional[int] = None,
    dedupe_key: str = "",
) -> Outbox:
    with transaction.atomic():
        return Outbox.objects.create(
            event_key=event_key,
            payload=payload or {},
            website_id=website_id,
            user_id=user_id,
            dedupe_key=dedupe_key,
        )

def mark_processed(ob: Outbox, ok: bool, err: str = "") -> None:
    ob.attempts += 1
    ob.processed_at = timezone.now() if ok else None
    ob.last_error = err[:2000] if err else ""
    ob.save(update_fields=["attempts", "processed_at", "last_error"])