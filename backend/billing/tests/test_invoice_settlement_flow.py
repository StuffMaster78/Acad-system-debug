from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from billing.models.installment import PaymentInstallment
from billing.models.receipt import Receipt
from billing.models.reminder import Reminder
from billing.services.invoice_orchestration_service import (
    InvoiceOrchestrationService,
)
from billing.services.invoice_service import InvoiceService
from billing.services.payment_installment_service import (
    PaymentInstallmentService,
)
from billing.services.reminder_service import ReminderService
from payments_processor.models import PaymentIntent
from websites.models.websites import Website
from users.models import User
from billing.constants import InvoiceStatus, ReminderStatus


class InvoiceSettlementFlowTests(TestCase):
    """
    Verify invoice settlement side effects across billing concerns.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.com",
        )
        self.client_user = User.objects.create_user(
            username="clientuser",
            email="client@example.com",
            password="testpass123",
            website=self.website,
        )

        self.invoice = InvoiceService.create_invoice(
            website=self.website,
            title="Large special order",
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

        self.payment_intent = PaymentIntent.objects.create(
            reference="pay_intent_001",
            client=self.client_user,
            purpose="invoice",
            provider="paystack",
            status="pending",
            currency="USD",
            amount=Decimal("600.00"),
            payable_object_id=self.invoice.pk,
            metadata={},
        )

        self.invoice = InvoiceService.attach_payment_intent_reference(
            invoice=self.invoice,
            payment_intent_reference=self.payment_intent.reference,
        )

        ReminderService.create_reminder(
            website=self.website,
            invoice=self.invoice,
            channel="email",
            event_key="billing.invoice.reminder",
            scheduled_for=timezone.now() + timedelta(days=1),
        )

    @patch(
        "billing.services.invoice_orchestration_service."
        "PaymentProcessorLedgerService.post_external_payment_capture"
    )
    @patch(
        "billing.services.receipt_orchestration_service."
        "NotificationService.notify"
    )
    @patch(
        "billing.services.invoice_orchestration_service."
        "PaymentApplicationService.apply_payment"
    )
    def test_full_settlement_issues_receipt_and_cancels_reminders(
        self,
        mock_apply_payment,
        mock_receipt_notify,
        mock_post_ledger,
    ) -> None:
        """
        Full settlement should allocate installments, issue receipt,
        cancel reminders, and post external capture when present.
        """
        mock_apply_payment.return_value = {
            "settlement_result": {
                "fully_settled": True,
            }
        }

        result = InvoiceOrchestrationService.apply_verified_invoice_payment(
            invoice=self.invoice,
            payment_intent=self.payment_intent,
            total_amount=Decimal("600.00"),
            external_reference="ext_123",
            external_captured_amount=Decimal("600.00"),
            send_notification=False,
            triggered_by=self.client_user,
        )

        installments = list(
            PaymentInstallment.objects.filter(
                invoice=self.invoice
            ).order_by("sequence_number")
        )
        reminders = list(
            Reminder.objects.filter(invoice=self.invoice)
        )
        receipts = list(
            Receipt.objects.filter(invoice=self.invoice)
        )

        self.assertTrue(result.fully_settled)
        self.assertEqual(result.invoice.status, InvoiceStatus.PAID)
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0].amount, Decimal("600.00"))

        self.assertEqual(
            installments[0].amount_paid,
            Decimal("300.00"),
        )
        self.assertEqual(
            installments[1].amount_paid,
            Decimal("300.00"),
        )
        self.assertIsNotNone(installments[0].paid_at)
        self.assertIsNotNone(installments[1].paid_at)

        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0].status, ReminderStatus.CANCELLED)

        mock_post_ledger.assert_called_once()
        mock_receipt_notify.assert_called_once()