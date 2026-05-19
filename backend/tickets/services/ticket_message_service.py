from __future__ import annotations

from django.db import transaction

from communications.constants import CommunicationThreadKind
from communications.services.message_service import CommunicationMessageService
from communications.services.thread_service import CommunicationThreadService

from tickets.constants import TicketAction, TicketRole
from tickets.services.ticket_log_service import TicketLogService
from tickets.services.ticket_notification_service import TicketNotificationService
from tickets.services.ticket_sla_service import TicketSLAService


class TicketMessageService:
    """
    Ticket-facing wrapper around communications messages.
    """

    @classmethod
    @transaction.atomic
    def add_message(
        cls,
        *,
        ticket,
        sender,
        body: str,
        is_internal: bool = False,
        parent=None,
        metadata: dict | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
    ):
        cls._validate_internal_note(sender=sender, is_internal=is_internal)

        thread = cls.get_or_create_thread(ticket=ticket, actor=sender)
        message_metadata = {
            "ticket_id": ticket.id,
            "ticket_status": ticket.status,
            "ticket_category": ticket.category,
            **(metadata or {}),
        }

        if is_internal:
            message = CommunicationMessageService.create_internal_note(
                thread=thread,
                sender=sender,
                body=body,
                website=ticket.website,
                metadata=message_metadata,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        else:
            message = CommunicationMessageService.create_message(
                thread=thread,
                sender=sender,
                body=body,
                website=ticket.website,
                parent=parent,
                is_internal=False,
                metadata=message_metadata,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if cls._is_staff(sender):
            TicketSLAService.mark_first_response(ticket=ticket)

        TicketLogService.record(
            ticket=ticket,
            actor=sender,
            action=TicketAction.MESSAGE_ADDED,
            metadata={"communication_message_id": message.id},
        )
        TicketNotificationService.replied(
            ticket=ticket,
            message=message,
            actor=sender,
        )
        return message

    @classmethod
    def get_or_create_thread(cls, *, ticket, actor):
        return CommunicationThreadService.get_or_create_thread(
            target=ticket,
            thread_kind=CommunicationThreadKind.CLIENT_SUPPORT,
            created_by=actor,
            website=ticket.website,
        )

    @staticmethod
    def _is_staff(user) -> bool:
        return getattr(user, "role", None) in TicketRole.STAFF_ROLES

    @classmethod
    def _validate_internal_note(cls, *, sender, is_internal: bool) -> None:
        if is_internal and not cls._is_staff(sender):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Only staff can create internal notes.")
