"""
Notification async worker.
Handles event → notification outbox transformation.
"""

from __future__ import annotations

import hashlib
import logging

from celery import shared_task
from django.conf import settings

from notifications_system.enums import (
    NotificationPriority,
    is_valid_event,
    get_event_category,
)

from users_state.tasks.outbox_tasks import create_outbox_entry

logger = logging.getLogger(__name__)


@shared_task
def handle_notification_event(event_payload: dict) -> None:
    """
    Async notification processor.

    Converts domain events into outbox entries.
    """

    event_type = event_payload.get("type")
    user_id = event_payload.get("user_id")
    website_id = event_payload.get("website_id")

    if not event_type or not user_id or not website_id:
        logger.warning("Invalid notification payload: %s", event_payload)
        return

    if not getattr(settings, "ENABLE_NOTIFICATIONS", True):
        return

    if not is_valid_event(event_type):
        logger.warning("Unknown event type: %s", event_type)
        return

    payload = {
        "event_key": event_type,
        "recipient_id": user_id,
        "website_id": website_id,
        "context": event_payload.get("context", {}),
        "channels": ["in_app"],
        "priority": NotificationPriority.NORMAL,
        "is_critical": False,
        "is_silent": False,
        "is_digest": False,
        "is_broadcast": False,
        "digest_group": None,
        "triggered_by_id": event_payload.get("actor_id"),
        "category": get_event_category(event_type),
        "dedupe_key": _build_dedupe_key(
            event_type,
            user_id,
            website_id,
        ),
    }

    create_outbox_entry.delay(payload)  # type: ignore[attr-defined]


def _build_dedupe_key(event_key: str, user_id: int, website_id: int) -> str:
    raw = f"{event_key}:{user_id}:{website_id}"
    return hashlib.sha256(raw.encode()).hexdigest()