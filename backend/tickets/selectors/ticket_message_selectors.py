from __future__ import annotations

from communications.constants import CommunicationThreadKind
from communications.models import CommunicationMessage, CommunicationThread
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class TicketMessageSelector:
    """
    Read helpers for communication messages attached to tickets.
    """

    @classmethod
    def for_ticket_visible_to_user(cls, *, ticket, user):
        thread = cls.thread_for_ticket(ticket=ticket)
        if thread is None:
            return CommunicationMessage.objects.none()

        CommunicationThreadGuardService.enforce_can_view_thread(
            user=user,
            website=ticket.website,
            thread=thread,
        )

        qs = CommunicationMessage.objects.filter(
            website=ticket.website,
            thread=thread,
        ).select_related("sender", "thread")

        if getattr(user, "role", None) not in {
            "admin",
            "superadmin",
            "support",
            "editor",
        }:
            qs = qs.filter(is_internal=False)

        return qs.order_by("created_at", "id")

    @staticmethod
    def thread_for_ticket(*, ticket):
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(
            ticket,
            for_concrete_model=False,
        )
        return CommunicationThread.objects.filter(
            website=ticket.website,
            target_content_type=content_type,
            target_object_id=ticket.id,
            kind=CommunicationThreadKind.CLIENT_SUPPORT,
        ).first()
