from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


class SpecialOrderAuditService:
    """
    Adapter for special order audit events.

    Delegates to the central AuditService with special-order context.
    Keeping calls isolated here means callers never import AuditService
    directly and the audit implementation can evolve independently.
    """

    @staticmethod
    def record(
        *,
        event_key: str,
        special_order,
        actor=None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an audit event for a special order action.

        Swallows all exceptions so an audit failure never rolls back
        the calling service transaction.
        """
        try:
            from audit_logging.services.audit_service import AuditService

            AuditService.record(
                action=event_key,
                actor=actor,
                website=special_order.website,
                obj=special_order,
                metadata=metadata or {},
                service_name="special_orders",
            )
        except Exception as exc:
            log.warning(
                "SpecialOrderAuditService.record failed event_key=%s "
                "special_order=%s: %s",
                event_key,
                getattr(special_order, "pk", None),
                exc,
            )