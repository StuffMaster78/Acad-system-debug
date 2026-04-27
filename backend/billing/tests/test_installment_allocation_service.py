from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from billing.models.installment import PaymentInstallment
from billing.services.installment_allocation_service import (
    InstallmentAllocationService,
)
from billing.services.payment_installment_service import (
    PaymentInstallmentService,
)
from billing.services.invoice_service import InvoiceService
from websites.models.websites import Website
from users.models import User


class InstallmentAllocationServiceTests(TestCase):
    """
    Verify installment allocation behavior for invoice payments.
    """

    def setUp(self) -> None:
        """
        Build a tenant, client, invoice, and installment schedule.
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
            title="Large special order",
            amount=Decimal("900.00"),
            due_at=timezone.now() + timedelta(days=10),
            issued_by=self.client_user,
            purpose="special_order",
            client=self.client_user,
            recipient_email=self.client_user.email,
            recipient_name="Client User",
            currency="USD",
        )

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
                {
                    "sequence_number": 3,
                    "amount": Decimal("300.00"),
                    "due_at": timezone.now() + timedelta(days=8),
                },
            ],
        )

    def test_allocates_to_earliest_unpaid_installment_first(self) -> None:
        """
        A payment should satisfy the earliest unpaid installment first.
        """
        result = (
            InstallmentAllocationService
            .allocate_payment_to_invoice_installments(
                invoice=self.invoice,
                amount=Decimal("300.00"),
            )
        )

        installments = list(
            PaymentInstallment.objects.filter(
                invoice=self.invoice
            ).order_by("sequence_number")
        )

        self.assertEqual(result.total_applied, Decimal("300.00"))
        self.assertEqual(result.remaining_unapplied, Decimal("0.00"))

        self.assertEqual(
            installments[0].amount_paid,
            Decimal("300.00"),
        )
        self.assertIsNotNone(installments[0].paid_at)

        self.assertEqual(
            installments[1].amount_paid,
            Decimal("0.00"),
        )
        self.assertIsNone(installments[1].paid_at)

    def test_rolls_over_to_next_installment(self) -> None:
        """
        Allocation should continue into the next installment when the
        payment exceeds the first installment balance.
        """
        result = (
            InstallmentAllocationService
            .allocate_payment_to_invoice_installments(
                invoice=self.invoice,
                amount=Decimal("450.00"),
            )
        )

        installments = list(
            PaymentInstallment.objects.filter(
                invoice=self.invoice
            ).order_by("sequence_number")
        )

        self.assertEqual(result.total_applied, Decimal("450.00"))
        self.assertEqual(result.remaining_unapplied, Decimal("0.00"))

        self.assertEqual(
            installments[0].amount_paid,
            Decimal("300.00"),
        )
        self.assertEqual(
            installments[1].amount_paid,
            Decimal("150.00"),
        )
        self.assertEqual(
            installments[2].amount_paid,
            Decimal("0.00"),
        )

        self.assertIsNotNone(installments[0].paid_at)
        self.assertIsNone(installments[1].paid_at)

    def test_rejects_non_positive_allocation_amount(self) -> None:
        """
        Allocation should reject zero or negative amounts.
        """
        with self.assertRaisesMessage(
            Exception,
            "Allocation amount must be greater than zero.",
        ):
            InstallmentAllocationService.allocate_payment_to_invoice_installments(
                invoice=self.invoice,
                amount=Decimal("0.00"),
            )