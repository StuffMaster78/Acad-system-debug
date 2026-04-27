from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from billing.models.reminder import Reminder
from billing.services.invoice_service import InvoiceService
from billing.services.payment_installment_service import (
    PaymentInstallmentService,
)
from billing.services.reminder_orchestration_service import (
    ReminderOrchestrationService,
)
from billing.services.reminder_service import ReminderService
from websites.models.websites import Website
from users.models import User
from billing.constants import ReminderStatus


class ReminderOrchestrationServiceTests(TestCase):
    """
    Verify reminder idempotency, dispatch, and installment-aware
    behavior.
    """

    def setUp(self) -> None:
        """
        Build tenant, client, invoice, and one installment.
        """
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.com",
        )
        self.client_user = User.objects.create_user(
            username="testuser",
            email="client@example.com",
            password="testpass123",
            website=self.website,
        )
        self.invoice = InvoiceService.create_invoice(
            website=self.website,
            title="Installment invoice",
            amount=Decimal("600.00"),
            due_at=timezone.now() + timedelta(days=10),
            issued_by=self.client_user,
            purpose="special_order",
            client=self.client_user,
            recipient_email=self.client_user.email,
            recipient_name="Client User",
            currency="USD",
        )
        self.invoice = InvoiceService.issue_invoice(invoice=self.invoice)

        PaymentInstallmentService.create_schedule(
            invoice=self.invoice,
            schedule=[
                {
                    "sequence_number": 1,
                    "amount": Decimal("300.00"),
                    "due_at": timezone.now() + timedelta(days=2),
                },
                {
                    "sequence_number": 2,
                    "amount": Decimal("300.00"),
                    "due_at": timezone.now() + timedelta(days=5),
                },
            ],
        )

    @patch("billing.services.reminder_orchestration_service.AuditLogService.log")
    def test_ensure_invoice_reminder_is_idempotent(
        self,
        mock_audit_log,
    ) -> None:
        """
        Repeated ensure calls should return the same pending reminder.
        """
        scheduled_for = timezone.now() + timedelta(days=1)

        reminder_one = ReminderOrchestrationService.ensure_invoice_reminder(
            invoice=self.invoice,
            event_key="billing.invoice.reminder",
            scheduled_for=scheduled_for,
            triggered_by=self.client_user,
        )
        reminder_two = ReminderOrchestrationService.ensure_invoice_reminder(
            invoice=self.invoice,
            event_key="billing.invoice.reminder",
            scheduled_for=scheduled_for,
            triggered_by=self.client_user,
        )

        self.assertEqual(reminder_one.pk, reminder_two.pk)
        self.assertEqual(
            Reminder.objects.filter(invoice=self.invoice).count(),
            1,
        )
        self.assertEqual(mock_audit_log.call_count, 1)

    @patch("billing.services.reminder_orchestration_service.AuditLogService.log")
    @patch(
        "billing.services.reminder_orchestration_service.NotificationService.notify"
    )
    def test_dispatch_reminder_marks_sent_on_success(
        self,
        mock_notify,
        mock_audit_log,
    ) -> None:
        """
        Successful dispatch should mark the reminder as sent.
        """
        reminder = ReminderService.create_reminder(
            website=self.website,
            invoice=self.invoice,
            channel="email",
            event_key="billing.invoice.reminder",
            scheduled_for=timezone.now(),
        )

        updated = ReminderOrchestrationService.dispatch_reminder(
            reminder=reminder,
            triggered_by=self.client_user,
        )

        self.assertEqual(updated.status, ReminderStatus.SENT)
        self.assertIsNotNone(updated.sent_at)
        mock_notify.assert_called_once()
        self.assertGreaterEqual(mock_audit_log.call_count, 1)

    @patch("billing.services.reminder_orchestration_service.AuditLogService.log")
    @patch(
        "billing.services.reminder_orchestration_service.NotificationService.notify"
    )
    def test_dispatch_reminder_marks_failed_on_notify_error(
        self,
        mock_notify,
        mock_audit_log,
    ) -> None:
        """
        Notification failure should mark the reminder as failed.
        """
        mock_notify.side_effect = RuntimeError("SMTP exploded")

        reminder = ReminderService.create_reminder(
            website=self.website,
            invoice=self.invoice,
            channel="email",
            event_key="billing.invoice.reminder",
            scheduled_for=timezone.now(),
        )

        updated = ReminderOrchestrationService.dispatch_reminder(
            reminder=reminder,
            triggered_by=self.client_user,
        )

        self.assertEqual(updated.status, ReminderStatus.FAILED)
        self.assertIn("SMTP exploded", updated.error_message)
        self.assertGreaterEqual(mock_audit_log.call_count, 1)

    @patch("billing.services.reminder_orchestration_service.AuditLogService.log")
    @patch(
        "billing.services.reminder_orchestration_service.NotificationService.notify"
    )
    def test_dispatch_installment_reminder_uses_installment_context(
        self,
        mock_notify,
        mock_audit_log,
    ) -> None:
        """
        Installment reminder dispatch should include installment payload
        in notification context.
        """
        reminder = ReminderService.create_reminder(
            website=self.website,
            invoice=self.invoice,
            channel="email",
            event_key="billing.installment.upcoming",
            scheduled_for=timezone.now(),
        )

        ReminderOrchestrationService.dispatch_reminder(
            reminder=reminder,
            triggered_by=self.client_user,
        )

        _, kwargs = mock_notify.call_args
        context = kwargs["context"]

        self.assertIn("installment_id", context)
        self.assertIn("installment_sequence_number", context)
        self.assertIn("installment_due_at", context)
        self.assertGreaterEqual(mock_audit_log.call_count, 1)