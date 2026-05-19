from __future__ import annotations

from django.db.models import Q, QuerySet

from tickets.constants import TicketRole
from tickets.models import Ticket


class TicketSelector:
    """
    Read helpers for tickets.
    """

    @classmethod
    def base(cls) -> QuerySet[Ticket]:
        return Ticket.objects.select_related(
            "created_by",
            "assigned_to",
            "website",
            "content_type",
        )

    @classmethod
    def visible_to_user(cls, *, user) -> QuerySet[Ticket]:
        qs = cls.base()
        role = getattr(user, "role", None)

        if role in TicketRole.USER_ROLES:
            return qs.filter(
                Q(created_by=user)
                | Q(assigned_to=user)
            ).distinct()

        website_id = getattr(user, "website_id", None)
        if website_id and role not in {"superadmin"}:
            qs = qs.filter(website_id=website_id)

        return qs

    @classmethod
    def detail_visible_to_user(cls, *, user) -> QuerySet[Ticket]:
        return cls.visible_to_user(user=user).prefetch_related("logs")
