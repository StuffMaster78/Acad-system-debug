from __future__ import annotations

from typing import Any


class ActivityAuditLoggingIntegration:
    """
    Optional bridge between activity and audit logging.

    Activity remains user and product focused. Audit logging remains the
    forensic record. This bridge exists only for workflows that need both.
    """

    @staticmethod
    def record_related_audit_event(
        *,
        actor,
        target,
        action: str,
        website,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a related audit event if the audit app exposes a service.

        This method is intentionally defensive because audit logging
        implementations often differ by project stage.
        
        Activity remains user and product focused. Audit logging remains the
        forensic record. This bridge exists only for workflows that need both.
        """
        try:
            from audit_logging.services.audit_service import (
                AuditService,
            )
        except ImportError:
            return

        AuditService.record(
            actor=actor,
            obj=target,
            action=action,
            website=website,
            metadata=metadata or {},
        )