from __future__ import annotations

from tickets.sla_timers import TicketSLA


class TicketSLASelector:
    @classmethod
    def visible_to_user(cls, *, user):
        qs = TicketSLA.objects.select_related(
            "ticket",
            "ticket__created_by",
            "website",
        )

        website_id = getattr(user, "website_id", None)
        if website_id and getattr(user, "role", None) != "superadmin":
            qs = qs.filter(website_id=website_id)

        if getattr(user, "role", None) in {"client", "writer"}:
            qs = qs.filter(ticket__created_by=user)

        return qs.order_by("-resolution_deadline")
