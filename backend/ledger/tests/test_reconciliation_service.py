from decimal import Decimal

from django.test import TestCase

from ledger.constants import ReconciliationStatus
from ledger.services.ledger_reconciliation_service import (
    LedgerReconciliationService,
)
from users.models import User
from websites.models.websites import Website


class LedgerReconciliationServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="recon@example.com",
            password="password123",
            website=self.website,
        )

    def test_create_record_creates_unreconciled_record(self) -> None:
        record = LedgerReconciliationService.create_record(
            website=self.website,
            expected_amount=Decimal("1000.00"),
            user=self.user,
            reference="PAY-1",
        )

        self.assertEqual(record.status, ReconciliationStatus.UNRECONCILED)
        self.assertEqual(record.expected_amount, Decimal("1000.00"))
        self.assertEqual(record.matched_amount, Decimal("0.00"))

    def test_reconcile_exact_amount_marks_record_matched(self) -> None:
        record = LedgerReconciliationService.create_record(
            website=self.website,
            expected_amount=Decimal("1000.00"),
            user=self.user,
            reference="PAY-2",
        )

        record = LedgerReconciliationService.reconcile(
            record=record,
            actual_amount=Decimal("1000.00"),
        )

        self.assertEqual(record.status, ReconciliationStatus.MATCHED)
        self.assertEqual(record.variance_amount, Decimal("0.00"))

    def test_reconcile_partial_amount_marks_record_partially_matched(
        self,
    ) -> None:
        record = LedgerReconciliationService.create_record(
            website=self.website,
            expected_amount=Decimal("1000.00"),
            user=self.user,
            reference="PAY-3",
        )

        record = LedgerReconciliationService.reconcile(
            record=record,
            actual_amount=Decimal("600.00"),
        )

        self.assertEqual(
            record.status,
            ReconciliationStatus.PARTIALLY_MATCHED,
        )
        self.assertEqual(record.actual_amount, Decimal("600.00"))