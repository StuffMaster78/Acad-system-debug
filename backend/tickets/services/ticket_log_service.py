from __future__ import annotations

from tickets.models import TicketLog


class TicketLogService:
    """
    Central writer for ticket audit log rows.
    """

    @classmethod
    def record(
        cls,
        *,
        ticket,
        action: str,
        actor=None,
        metadata: dict | None = None,
    ) -> TicketLog:
        details = action
        if metadata:
            details = f"{action}: {metadata}"

        return TicketLog.objects.create(
            ticket=ticket,
            website=ticket.website,
            action=details,
            performed_by=actor,
        )
