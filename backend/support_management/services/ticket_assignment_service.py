from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Optional

from django.db import transaction
from django.utils import timezone

log = logging.getLogger(__name__)

# Default SLA window for tickets by priority.
_SLA_HOURS_BY_PRIORITY = {
    "critical": 4,
    "high": 8,
    "medium": 24,
    "low": 48,
}


class TicketAssignmentService:
    """
    Routes support tickets to agents and manages SLA creation.

    This service is the single point of truth for initial ticket
    assignment and manual reassignment. Auto-reassignment of stale
    or overloaded queues is handled by SmartReassignmentService.

    Responsibilities:
        1. Assign an unassigned ticket to the best available agent.
        2. Manually reassign a ticket from one agent to another.
        3. Create OrderDisputeSLA records on assignment.
        4. Notify the assigned agent.
        5. Record SupportActivityLog entries.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def assign(
        cls,
        *,
        ticket,
        assigned_by,
        agent=None,
        reason: str = "",
    ):
        """
        Assign a ticket to an agent.

        If agent is None, the best available agent is selected
        automatically using SmartReassignmentService.

        Args:
            ticket: Ticket instance to assign.
            assigned_by: Staff member performing the assignment.
            agent: Optional explicit agent user to assign to.
            reason: Optional reason (recorded in activity log).

        Returns:
            Updated ticket instance.

        Raises:
            ValueError: If no available agent can be found.
        """
        if agent is None:
            agent = cls._find_best_agent(ticket=ticket)

        if agent is None:
            raise ValueError(
                "No available support agent found for ticket assignment."
            )

        ticket.assigned_to = agent
        if ticket.status == "open":
            ticket.status = "in_progress"
        ticket.save(update_fields=["assigned_to", "status", "updated_at"])

        cls._create_sla(ticket=ticket, assigned_to=agent)
        cls._log_activity(
            ticket=ticket,
            agent=agent,
            assigned_by=assigned_by,
            action="assigned",
            reason=reason,
        )
        cls._notify_agent(ticket=ticket, agent=agent)

        return ticket

    @classmethod
    @transaction.atomic
    def reassign(
        cls,
        *,
        ticket,
        new_agent,
        reassigned_by,
        reason: str = "",
    ):
        """
        Reassign a ticket from its current agent to a different one.

        Args:
            ticket: Ticket to reassign.
            new_agent: New agent user.
            reassigned_by: Staff member performing the reassignment.
            reason: Required reason for the reassignment.

        Returns:
            Updated ticket instance.
        """
        previous_agent = ticket.assigned_to

        ticket.assigned_to = new_agent
        ticket.save(update_fields=["assigned_to", "updated_at"])

        cls._update_sla_assignment(ticket=ticket, agent=new_agent)
        cls._log_activity(
            ticket=ticket,
            agent=new_agent,
            assigned_by=reassigned_by,
            action="reassigned",
            reason=reason,
            previous_agent=previous_agent,
        )
        cls._notify_agent(ticket=ticket, agent=new_agent)

        log.info(
            "Ticket %s reassigned from %s to %s by %s",
            ticket.pk,
            getattr(previous_agent, "pk", None),
            getattr(new_agent, "pk", None),
            getattr(reassigned_by, "pk", None),
        )

        return ticket

    @classmethod
    @transaction.atomic
    def unassign(cls, *, ticket, unassigned_by, reason: str = ""):
        """
        Remove the current agent assignment from a ticket.

        Puts the ticket back to 'open' status.
        """
        ticket.assigned_to = None
        ticket.status = "open"
        ticket.save(update_fields=["assigned_to", "status", "updated_at"])

        cls._log_activity(
            ticket=ticket,
            agent=None,
            assigned_by=unassigned_by,
            action="unassigned",
            reason=reason,
        )
        return ticket

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_best_agent(*, ticket):
        """Use SmartReassignmentService to find the lowest-load agent."""
        try:
            from support_management.services.reassignment_service import (
                SmartReassignmentService,
            )
            return SmartReassignmentService.find_best_available_agent(
                sla_type="ticket"
            )
        except Exception as exc:
            log.warning("_find_best_agent failed for ticket=%s: %s", ticket.pk, exc)
            return None

    @staticmethod
    def _create_sla(*, ticket, assigned_to) -> None:
        """Create an OrderDisputeSLA for the ticket if SLA is enabled."""
        try:
            from support_management.models import OrderDisputeSLA

            hours = _SLA_HOURS_BY_PRIORITY.get(
                getattr(ticket, "priority", "medium"), 24
            )
            expected = timezone.now() + timedelta(hours=hours)

            OrderDisputeSLA.objects.update_or_create(
                order=None,
                dispute=None,
                defaults={
                    "sla_type": "order_resolution",
                    "assigned_to": assigned_to,
                    "expected_resolution_time": expected,
                    "status": "on_track",
                },
            )

            ticket.has_sla = True
            ticket.save(update_fields=["has_sla"])
        except Exception as exc:
            log.warning("_create_sla failed for ticket=%s: %s", ticket.pk, exc)

    @staticmethod
    def _update_sla_assignment(*, ticket, agent) -> None:
        """Reassign the SLA record to the new agent."""
        try:
            from support_management.models import OrderDisputeSLA

            OrderDisputeSLA.objects.filter(
                assigned_to__isnull=False,
            ).filter(
                status__in=["on_track", "warning"],
            ).update(assigned_to=agent)
        except Exception as exc:
            log.warning(
                "_update_sla_assignment failed for ticket=%s: %s", ticket.pk, exc
            )

    @staticmethod
    def _log_activity(
        *,
        ticket,
        agent,
        assigned_by,
        action: str,
        reason: str = "",
        previous_agent=None,
    ) -> None:
        try:
            from support_management.models import SupportActivityLog

            description = (
                f"Ticket #{ticket.pk} {action} to "
                f"{getattr(agent, 'email', 'unassigned')}"
            )
            if previous_agent:
                description += (
                    f" (previously: {getattr(previous_agent, 'email', 'none')})"
                )
            if reason:
                description += f". Reason: {reason}"

            SupportActivityLog.objects.create(
                user=assigned_by,
                action_type="updated_order_status",
                related_ticket=ticket,
                description=description,
            )
        except Exception as exc:
            log.warning("_log_activity failed for ticket=%s: %s", ticket.pk, exc)

    @staticmethod
    def _notify_agent(*, ticket, agent) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key="ticket.assigned",
                recipient=agent,
                website=ticket.website,
                context={
                    "ticket_id": ticket.pk,
                    "ticket_title": ticket.title,
                    "ticket_priority": getattr(ticket, "priority", ""),
                    "ticket_status": getattr(ticket, "status", ""),
                    "assigned_to_id": getattr(agent, "pk", None),
                },
            )
        except Exception as exc:
            log.warning("_notify_agent failed for ticket=%s: %s", ticket.pk, exc)
