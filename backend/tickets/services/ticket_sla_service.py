from __future__ import annotations

from tickets.sla_timers import TicketSLA


class TicketSLAService:
    """
    Service wrapper for ticket SLA state.
    """

    @classmethod
    def ensure_for_ticket(cls, *, ticket) -> TicketSLA:
        sla, created = TicketSLA.objects.get_or_create(
            ticket=ticket,
            defaults=cls._defaults(ticket=ticket),
        )
        if created and not ticket.has_sla:
            ticket.has_sla = True
            ticket.save(update_fields=["has_sla", "updated_at"])
        return sla

    @classmethod
    def mark_first_response(cls, *, ticket) -> None:
        sla = cls.ensure_for_ticket(ticket=ticket)
        sla.mark_first_response()

    @classmethod
    def mark_resolved(cls, *, ticket) -> None:
        sla = cls.ensure_for_ticket(ticket=ticket)
        sla.mark_resolved()

    @classmethod
    def check_breaches(cls, *, queryset) -> int:
        updated_count = 0
        for sla in queryset:
            old_breached = sla.resolution_breached
            sla.check_and_update_breaches()
            if sla.resolution_breached != old_breached:
                updated_count += 1
        return updated_count

    @staticmethod
    def _defaults(*, ticket) -> dict:
        from django.utils import timezone

        hours = TicketSLA.PRIORITY_SLA_HOURS.get(ticket.priority, 24)
        now = timezone.now()
        return {
            "website": ticket.website,
            "priority": ticket.priority,
            "first_response_deadline": now + timezone.timedelta(hours=hours // 2),
            "resolution_deadline": now + timezone.timedelta(hours=hours),
        }
