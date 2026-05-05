from __future__ import annotations

from typing import Any


class SpecialOrderAuditService:
    """
    Adapter for special order audit events.

    Replace the body of `record` with your central audit logging service.
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
        Record an audit event.

        Intentionally isolated so the app does not depend directly on
        audit implementation details everywhere.
        """
        # TODO:
        # Replace with your central audit service, for example:
        #
        # AuditLogService.record(
        #     event_key=event_key,
        #     website=special_order.website,
        #     actor=actor,
        #     target=special_order,
        #     metadata=metadata or {},
        # )
        return None