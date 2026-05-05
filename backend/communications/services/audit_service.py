from __future__ import annotations

from typing import Any

from communications.models.audit import CommunicationAuditLog


class CommunicationAuditService:
    """
    Write audit records for important communication actions.
    """

    @staticmethod
    def log(
        *,
        website,
        thread,
        action: str,
        actor=None,
        message=None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
    ) -> CommunicationAuditLog:
        """
        Create an immutable communication audit log entry.
        """
        return CommunicationAuditLog.objects.create(
            website=website,
            thread=thread,
            message=message,
            actor=actor,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )