"""
Tests for DisputeResolutionService.
"""
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from support_management.services.dispute_resolution_service import (
    DisputeResolutionService,
)
from websites.models.websites import Website

User = get_user_model()


def _make_dispute(status="open"):
    d = MagicMock()
    d.pk = 1
    d.status = status
    d.save = MagicMock()
    order = MagicMock()
    order.pk = 10
    d.order = order
    return d


class DisputeResolutionServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="DR", domain="dr.local")
        self.agent = User.objects.create_user(
            username="dr_agent", email="a@dr.local", password="x",
            website=self.website, is_staff=True,
        )

    def test_assign_updates_dispute_agent(self):
        dispute = _make_dispute()
        with patch.object(DisputeResolutionService, "_log_activity"):
            with patch.object(DisputeResolutionService, "_notify_agent"):
                DisputeResolutionService.assign(
                    dispute=dispute, agent=self.agent,
                    assigned_by=self.agent,
                )
        dispute.save.assert_called_once()
        self.assertEqual(dispute.assigned_to, self.agent)

    def test_resolve_raises_on_empty_notes(self):
        dispute = _make_dispute()
        with self.assertRaises(ValidationError):
            DisputeResolutionService.resolve(
                dispute=dispute, resolved_by=self.agent,
                resolution="Resolved", notes="",
            )

    def test_resolve_raises_on_already_closed_dispute(self):
        dispute = _make_dispute(status="resolved")
        with self.assertRaises(ValidationError):
            DisputeResolutionService.resolve(
                dispute=dispute, resolved_by=self.agent,
                resolution="Done", notes="Some notes",
            )

    def test_resolve_calls_mark_dispute_resolved(self):
        dispute = _make_dispute()
        with patch.object(
            DisputeResolutionService, "_mark_dispute_resolved",
        ) as mock_resolve:
            with patch.object(DisputeResolutionService, "_create_resolution_log"):
                with patch.object(DisputeResolutionService, "_log_activity"):
                    with patch.object(DisputeResolutionService, "_notify_parties"):
                        DisputeResolutionService.resolve(
                            dispute=dispute, resolved_by=self.agent,
                            resolution="Client wins", notes="Evidence reviewed",
                        )
        mock_resolve.assert_called_once()

    def test_escalate_raises_on_empty_reason(self):
        dispute = _make_dispute()
        with self.assertRaises(ValidationError):
            DisputeResolutionService.escalate(
                dispute=dispute, escalated_by=self.agent,
                reason="", website=self.website,
            )
