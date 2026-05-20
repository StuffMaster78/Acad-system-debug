from __future__ import annotations

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from tickets.api.exceptions import TicketTransitionError
from tickets.constants import TicketAction, TicketRole
from tickets.models import Ticket
from tickets.services.ticket_log_service import TicketLogService
from tickets.services.ticket_notification_service import TicketNotificationService
from tickets.services.ticket_sla_service import TicketSLAService


class TicketService:
    """
    Business actions for support tickets.
    """

    @classmethod
    @transaction.atomic
    def create_ticket(
        cls,
        *,
        actor,
        title: str,
        description: str,
        website=None,
        priority: str = "medium",
        category: str = "general",
        created_by=None,
        related_object=None,
    ) -> Ticket:
        requester = created_by if cls._is_staff(actor) and created_by else actor
        resolved_website = website or cls._resolve_website(user=requester)

        ticket = Ticket.objects.create(
            title=title,
            description=description,
            created_by=requester,
            website=resolved_website,
            priority=priority,
            category=category,
        )

        if related_object is not None:
            ticket.content_type = ContentType.objects.get_for_model(
                related_object,
                for_concrete_model=False,
            )
            ticket.object_id = related_object.pk
            ticket.save(update_fields=["content_type", "object_id", "updated_at"])

        TicketSLAService.ensure_for_ticket(ticket=ticket)
        TicketLogService.record(
            ticket=ticket,
            actor=actor,
            action=TicketAction.CREATED,
        )
        TicketNotificationService.created(ticket=ticket, actor=actor)
        return ticket

    @classmethod
    @transaction.atomic
    def assign(cls, *, ticket, assigned_to, actor) -> Ticket:
        old_assignee_id = ticket.assigned_to_id
        ticket.assigned_to = assigned_to
        ticket.save(update_fields=["assigned_to", "updated_at"])

        TicketLogService.record(
            ticket=ticket,
            actor=actor,
            action=TicketAction.ASSIGNED,
            metadata={
                "old_assigned_to_id": old_assignee_id,
                "assigned_to_id": assigned_to.id if assigned_to else None,
            },
        )
        TicketNotificationService.assigned(ticket=ticket, actor=actor)
        return ticket

    @classmethod
    @transaction.atomic
    def escalate(cls, *, ticket, actor) -> Ticket:
        old_priority = ticket.priority
        ticket.is_escalated = True
        ticket.priority = "critical"
        ticket.status = "escalated"
        ticket.save(
            update_fields=[
                "is_escalated",
                "priority",
                "status",
                "updated_at",
            ],
        )
        TicketLogService.record(
            ticket=ticket,
            actor=actor,
            action=TicketAction.ESCALATED,
            metadata={"old_priority": old_priority},
        )
        TicketNotificationService.escalated(ticket=ticket, actor=actor)
        return ticket

    @classmethod
    @transaction.atomic
    def close(cls, *, ticket, actor, reason: str = "") -> Ticket:
        old_status = ticket.status
        ticket.status = "closed"
        ticket.resolution_time = timezone.now()
        ticket.save(update_fields=["status", "resolution_time", "updated_at"])

        TicketSLAService.mark_resolved(ticket=ticket)
        TicketLogService.record(
            ticket=ticket,
            actor=actor,
            action=TicketAction.CLOSED,
            metadata={"reason": reason, "old_status": old_status},
        )
        TicketNotificationService.status_changed(
            ticket=ticket,
            actor=actor,
            old_status=old_status,
        )
        return ticket

    @classmethod
    @transaction.atomic
    def reopen(
        cls,
        *,
        ticket,
        actor,
        status: str = "open",
        reason: str = "",
    ) -> Ticket:
        if ticket.status != "closed":
            raise TicketTransitionError(
                f'Only closed tickets can be reopened. Current status: "{ticket.status}".'
            )

        if status not in {"open", "in_progress"}:
            raise TicketTransitionError(
                'Reopened tickets must move to "open" or "in_progress".'
            )

        old_status = ticket.status
        ticket.status = status
        ticket.resolution_time = None
        ticket.save(update_fields=["status", "resolution_time", "updated_at"])

        TicketLogService.record(
            ticket=ticket,
            actor=actor,
            action=TicketAction.REOPENED,
            metadata={"reason": reason, "old_status": old_status},
        )
        TicketNotificationService.status_changed(
            ticket=ticket,
            actor=actor,
            old_status=old_status,
        )
        return ticket

    @staticmethod
    def _is_staff(user) -> bool:
        return getattr(user, "role", None) in TicketRole.STAFF_ROLES

    @staticmethod
    def _resolve_website(*, user):
        website = getattr(user, "website", None)
        if website is not None:
            return website

        website_id = getattr(user, "website_id", None)
        if website_id:
            from websites.models.websites import Website

            return Website.objects.get(id=website_id)

        from websites.models.websites import Website

        default_site = Website.objects.filter(is_active=True).first()
        if default_site is not None:
            return default_site

        return Website.objects.create(
            name="Default Support Website",
            domain="https://support.local",
            is_active=True,
        )
