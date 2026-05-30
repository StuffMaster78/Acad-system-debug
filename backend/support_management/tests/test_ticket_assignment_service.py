"""
Tests for TicketAssignmentService.
"""
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from support_management.services.ticket_assignment_service import (
    TicketAssignmentService,
)
from tickets.models import Ticket
from websites.models.websites import Website

User = get_user_model()


class TicketAssignmentServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="T", domain="t.local")
        self.agent = User.objects.create_user(
            username="agent1", email="a@t.local", password="x", website=self.website,
            is_staff=True,
        )
        self.agent2 = User.objects.create_user(
            username="agent2", email="b@t.local", password="x", website=self.website,
            is_staff=True,
        )
        self.client_user = User.objects.create_user(
            username="cli", email="c@t.local", password="x", website=self.website,
        )
        self.ticket = Ticket.objects.create(
            title="Bug", description="desc",
            website=self.website, created_by=self.client_user,
            status="open", priority="medium",
        )

    def test_assign_sets_assigned_to(self):
        TicketAssignmentService.assign(
            ticket=self.ticket, assigned_by=self.agent, agent=self.agent2,
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.agent2)

    def test_assign_changes_status_to_in_progress(self):
        TicketAssignmentService.assign(
            ticket=self.ticket, assigned_by=self.agent, agent=self.agent2,
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "in_progress")

    def test_reassign_updates_agent(self):
        TicketAssignmentService.assign(
            ticket=self.ticket, assigned_by=self.agent, agent=self.agent,
        )
        TicketAssignmentService.reassign(
            ticket=self.ticket, new_agent=self.agent2,
            reassigned_by=self.agent, reason="load balancing",
        )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.agent2)

    def test_unassign_clears_assignment(self):
        TicketAssignmentService.assign(
            ticket=self.ticket, assigned_by=self.agent, agent=self.agent,
        )
        TicketAssignmentService.unassign(
            ticket=self.ticket, unassigned_by=self.agent,
        )
        self.ticket.refresh_from_db()
        self.assertIsNone(self.ticket.assigned_to)
        self.assertEqual(self.ticket.status, "open")

    def test_assign_without_agent_uses_best_available(self):
        """When agent is None, SmartReassignmentService is consulted."""
        with patch(
            "support_management.services.ticket_assignment_service."
            "TicketAssignmentService._find_best_agent",
            return_value=self.agent,
        ):
            TicketAssignmentService.assign(
                ticket=self.ticket, assigned_by=self.agent,
            )
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.agent)

    def test_assign_raises_when_no_agent_found(self):
        with patch(
            "support_management.services.ticket_assignment_service."
            "TicketAssignmentService._find_best_agent",
            return_value=None,
        ):
            with self.assertRaises(ValueError):
                TicketAssignmentService.assign(
                    ticket=self.ticket, assigned_by=self.agent,
                )
