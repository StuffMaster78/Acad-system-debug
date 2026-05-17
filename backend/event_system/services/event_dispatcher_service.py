from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.conf import settings

from event_system.router.event_router import EventRouter
from event_system.models.event_outbox import EventOutbox
from audit_logging.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class EventDispatcherService:
    """
    Dispatches event outbox entries through a single registered handler.

    Architecture assumption:
    - 1 event_type → 1 handler
    - EventOutbox is the source of truth
    """

    @staticmethod
    def dispatch(
        *,
        event_type: str,
        payload: Dict[str, Any],
        tenant_id: Optional[int] = None,
        actor: Any = None,
        idempotency_key: Optional[str] = None,
    ) -> bool:

        if not getattr(settings, "ENABLE_EVENT_SYSTEM", True):
            return False

        if not event_type:
            return False

        enriched_payload = {
            "event_type": event_type,
            "tenant_id": tenant_id,
            "actor_id": getattr(actor, "id", None),
            "idempotency_key": idempotency_key,
            "data": payload or {},
        }

        # -------------------------
        # AUDIT (safe boundary)
        # -------------------------
        try:
            AuditService.record(
                action=event_type,
                actor=actor,
                website=None,
                obj=None,
                metadata=enriched_payload,
                idempotency_key=idempotency_key,
                service_name="event_dispatcher",
            )
        except Exception as exc:
            logger.exception("Audit failed: %s", exc)

        # -------------------------
        # OUTBOX CREATION (IMPORTANT SHIFT)
        # -------------------------
        outbox = EventOutbox.objects.create(
            event_type=event_type,
            tenant_id=tenant_id,
            payload=enriched_payload,
            idempotency_key=idempotency_key,
            status="pending",
        )

        # -------------------------
        # ROUTE SINGLE HANDLER
        # -------------------------
        handler = EventRouter.get(event_type)

        if not handler:
            logger.info("No handler registered for %s", event_type)
            return True

        try:
            handler(outbox)
            return True

        except Exception as exc:
            logger.exception(
                "Handler failed for %s: %s",
                event_type,
                exc,
            )

            outbox.status = "failed"
            outbox.save(update_fields=["status"])

            return False