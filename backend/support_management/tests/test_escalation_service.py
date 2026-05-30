"""
Tests for EscalationService.
"""
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from support_management.models import EscalationLog
from support_management.services.escalation_service import (
    EscalationService,
    VALID_ACTION_TYPES,
)
from websites.models.websites import Website

User = get_user_model()


class EscalationServiceCreateTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Esc", domain="esc.local")
        self.agent = User.objects.create_user(
            username="agent_esc", email="ag@esc.local", password="x",
            website=self.website, is_staff=True,
        )
        self.target = User.objects.create_user(
            username="target_esc", email="tg@esc.local", password="x",
            website=self.website,
        )

    def test_create_returns_pending_escalation(self):
        esc = EscalationService.create(
            escalated_by=self.agent,
            action_type="suspend_client",
            target_user=self.target,
            reason="Repeated chargebacks",
            website=self.website,
        )
        self.assertEqual(esc.status, "pending")
        self.assertEqual(esc.action_type, "suspend_client")

    def test_create_raises_on_invalid_action_type(self):
        with self.assertRaises(ValidationError):
            EscalationService.create(
                escalated_by=self.agent,
                action_type="invalid_action",
                target_user=self.target,
                reason="x",
                website=self.website,
            )

    def test_create_raises_on_empty_reason(self):
        with self.assertRaises(ValidationError):
            EscalationService.create(
                escalated_by=self.agent,
                action_type="suspend_client",
                target_user=self.target,
                reason="",
                website=self.website,
            )

    def test_all_valid_action_types_accepted(self):
        for action in VALID_ACTION_TYPES:
            esc = EscalationService.create(
                escalated_by=self.agent,
                action_type=action,
                target_user=self.target,
                reason=f"test {action}",
                website=self.website,
            )
            self.assertEqual(esc.status, "pending")


class EscalationServiceReviewTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Esc2", domain="esc2.local")
        self.agent = User.objects.create_user(
            username="agent_esc2", email="ag@esc2.local", password="x",
            website=self.website, is_staff=True,
        )
        self.admin = User.objects.create_user(
            username="admin_esc2", email="ad@esc2.local", password="x",
            website=self.website, is_staff=True, is_superuser=True,
        )
        self.target = User.objects.create_user(
            username="tgt_esc2", email="tg@esc2.local", password="x",
            website=self.website,
        )

    def _make_escalation(self, action="blacklist_client"):
        return EscalationService.create(
            escalated_by=self.agent,
            action_type=action,
            target_user=self.target,
            reason="Test reason",
            website=self.website,
        )

    def test_reject_marks_escalation_rejected(self):
        esc = self._make_escalation()
        EscalationService.reject(
            escalation=esc, rejected_by=self.admin, reason="Not sufficient evidence",
        )
        esc.refresh_from_db()
        self.assertEqual(esc.status, "rejected")

    def test_reject_raises_on_empty_reason(self):
        esc = self._make_escalation()
        with self.assertRaises(ValidationError):
            EscalationService.reject(escalation=esc, rejected_by=self.admin, reason="")

    def test_reject_raises_on_already_approved(self):
        esc = self._make_escalation()
        esc.status = "approved"
        esc.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            EscalationService.reject(escalation=esc, rejected_by=self.admin, reason="late")

    def test_approve_with_non_blacklist_action_does_not_crash(self):
        """approve() swallows downstream errors — escalation still marked approved."""
        esc = self._make_escalation(action="suspend_client")
        with patch(
            "support_management.services.escalation_service.EscalationService._suspend_user",
        ):
            EscalationService.approve(escalation=esc, approved_by=self.admin)
        esc.refresh_from_db()
        self.assertEqual(esc.status, "approved")
