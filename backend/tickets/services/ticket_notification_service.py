from __future__ import annotations

import logging

from notifications_system.services.notification_service import (
    NotificationService,
)

log = logging.getLogger(__name__)


class TicketNotificationService:
    """
    Notification boundary for ticket workflows.
    """

    @classmethod
    def notify(
        cls,
        *,
        event_key: str,
        ticket,
        recipient,
        actor=None,
        context: dict | None = None,
        priority: str = "normal",
    ) -> None:
        if recipient is None:
            return

        try:
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=ticket.website,
                context={
                    "ticket_id": ticket.id,
                    "ticket_number": f"#{ticket.id}",
                    "ticket_title": ticket.title,
                    "ticket_subject": ticket.title,
                    "ticket_status": ticket.status,
                    "ticket_category": ticket.category,
                    "ticket_priority": ticket.priority,
                    **(context or {}),
                },
                channels=["email", "in_app"],
                triggered_by=actor,
                priority=priority,
                is_broadcast=False,
                is_critical=priority == "high",
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            log.exception("Ticket notification failed: %s", exc)

    @classmethod
    def created(cls, *, ticket, actor) -> None:
        cls.notify(
            event_key="ticket.created",
            ticket=ticket,
            recipient=ticket.created_by,
            actor=actor,
        )

    @classmethod
    def assigned(cls, *, ticket, actor) -> None:
        cls.notify(
            event_key="ticket.assigned",
            ticket=ticket,
            recipient=ticket.assigned_to,
            actor=actor,
            context={"assigned_to_id": ticket.assigned_to_id},
        )

    @classmethod
    def replied(cls, *, ticket, message, actor) -> None:
        recipients = [ticket.created_by, ticket.assigned_to]
        for recipient in {user for user in recipients if user and user != actor}:
            cls.notify(
                event_key="ticket.comment_added",
                ticket=ticket,
                recipient=recipient,
                actor=actor,
                context={
                    "communication_message_id": message.id,
                    "commenter_name": cls._display_name(actor),
                    "response_message": message.body,
                    "message_preview": message.body[:160],
                },
                priority="high",
            )

    @classmethod
    def escalated(cls, *, ticket, actor) -> None:
        recipient = ticket.assigned_to or ticket.created_by
        cls.notify(
            event_key="ticket.escalated",
            ticket=ticket,
            recipient=recipient,
            actor=actor,
            context={"escalated_by": cls._display_name(actor)},
            priority="high",
        )

    @classmethod
    def status_changed(cls, *, ticket, actor, old_status: str) -> None:
        if ticket.created_by and ticket.created_by != actor:
            cls.notify(
                event_key=f"ticket.{ticket.status}",
                ticket=ticket,
                recipient=ticket.created_by,
                actor=actor,
                context={"old_status": old_status},
                priority="high",
            )

    @staticmethod
    def _display_name(user) -> str:
        if user is None:
            return "System"
        if hasattr(user, "get_full_name"):
            full_name = user.get_full_name()
            if full_name:
                return full_name
        return getattr(user, "username", None) or getattr(user, "email", str(user))
