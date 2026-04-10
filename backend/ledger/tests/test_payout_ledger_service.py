from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    JournalEntryStatus,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.models import JournalEntry, JournalLine, LedgerAccount
from ledger.services.payout_ledger_service import PayoutLedgerService
from users.models import User
from websites.models.websites import Website


class PayoutLedgerServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="payouttester",
            email="payout@example.com",
            password="password123",
            website=self.website,
        )

        self.platform_revenue = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_REVENUE",
            name="Platform Revenue",
            account_type=LedgerAccountType.REVENUE,
            currency="USD",
            is_system_account=True,
        )
        self.writer_payable = LedgerAccount.objects.create(
            website=self.website,
            code="WRITER_PAYABLE",
            name="Writer Payable",
            account_type=LedgerAccountType.LIABILITY,
            currency="USD",
            is_system_account=True,
        )
        self.platform_cash = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="USD",
            is_system_account=True,
        )
        self.fines_recovery = LedgerAccount.objects.create(
            website=self.website,
            code="FINES_RECOVERY",
            name="Fines Recovery",
            account_type=LedgerAccountType.REVENUE,
            currency="USD",
            is_system_account=True,
        )

    def test_post_writer_earning_creates_posted_entry(self) -> None:
        entry = PayoutLedgerService.post_writer_earning(
            website=self.website,
            amount=Decimal("1800.00"),
            writer_reference="writer_1",
            related_object_type="Order",
            related_object_id="501",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(
            entry.entry_type,
            LedgerEntryType.WRITER_EARNING_ACCRUAL,
        )
        self.assertEqual(entry.source_model, "Order")
        self.assertEqual(entry.source_object_id, "501")

        lines = list(
            JournalLine.objects.filter(
                journal_entry=entry,
            ).order_by("created_at", "id")
        )

        self.assertEqual(len(lines), 2)

        debit_line = next(
            line for line in lines if line.entry_side == EntrySide.DEBIT
        )
        credit_line = next(
            line for line in lines if line.entry_side == EntrySide.CREDIT
        )

        self.assertEqual(debit_line.ledger_account, self.platform_revenue)
        self.assertEqual(credit_line.ledger_account, self.writer_payable)
        self.assertEqual(debit_line.wallet_reference, "writer_1")
        self.assertEqual(credit_line.wallet_reference, "writer_1")
        self.assertEqual(debit_line.related_object_type, "Order")
        self.assertEqual(credit_line.related_object_type, "Order")
        self.assertEqual(debit_line.related_object_id, "501")
        self.assertEqual(credit_line.related_object_id, "501")

    def test_post_writer_payout_creates_posted_entry(self) -> None:
        entry = PayoutLedgerService.post_writer_payout(
            website=self.website,
            amount=Decimal("1200.00"),
            writer_reference="writer_2",
            payout_id="payout_33",
            external_reference="bank_txn_33",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.WRITER_PAYOUT)
        self.assertEqual(entry.source_model, "WriterPayment")
        self.assertEqual(entry.source_object_id, "payout_33")
        self.assertEqual(entry.external_reference, "bank_txn_33")

        lines = list(
            JournalLine.objects.filter(
                journal_entry=entry,
            ).order_by("created_at", "id")
        )

        self.assertEqual(len(lines), 2)

        debit_line = next(
            line for line in lines if line.entry_side == EntrySide.DEBIT
        )
        credit_line = next(
            line for line in lines if line.entry_side == EntrySide.CREDIT
        )

        self.assertEqual(debit_line.ledger_account, self.writer_payable)
        self.assertEqual(credit_line.ledger_account, self.platform_cash)
        self.assertEqual(debit_line.related_object_type, "WriterPayment")
        self.assertEqual(credit_line.related_object_type, "WriterPayment")
        self.assertEqual(debit_line.related_object_id, "payout_33")
        self.assertEqual(credit_line.related_object_id, "payout_33")
        self.assertEqual(debit_line.wallet_reference, "writer_2")
        self.assertEqual(credit_line.wallet_reference, "writer_2")

    def test_post_writer_fine_creates_posted_entry(self) -> None:
        entry = PayoutLedgerService.post_writer_fine(
            website=self.website,
            amount=Decimal("300.00"),
            writer_reference="writer_3",
            fine_id="fine_77",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.WRITER_FINE)
        self.assertEqual(entry.source_model, "Fine")
        self.assertEqual(entry.source_object_id, "fine_77")

        lines = list(
            JournalLine.objects.filter(
                journal_entry=entry,
            ).order_by("created_at", "id")
        )

        self.assertEqual(len(lines), 2)

        debit_line = next(
            line for line in lines if line.entry_side == EntrySide.DEBIT
        )
        credit_line = next(
            line for line in lines if line.entry_side == EntrySide.CREDIT
        )

        self.assertEqual(debit_line.ledger_account, self.writer_payable)
        self.assertEqual(credit_line.ledger_account, self.fines_recovery)
        self.assertEqual(debit_line.related_object_type, "Fine")
        self.assertEqual(credit_line.related_object_type, "Fine")
        self.assertEqual(debit_line.related_object_id, "fine_77")
        self.assertEqual(credit_line.related_object_id, "fine_77")
        self.assertEqual(debit_line.wallet_reference, "writer_3")
        self.assertEqual(credit_line.wallet_reference, "writer_3")

    def test_payout_service_creates_expected_entries(self) -> None:
        PayoutLedgerService.post_writer_earning(
            website=self.website,
            amount=Decimal("1000.00"),
            writer_reference="writer_a",
            related_object_type="Order",
            related_object_id="1",
            triggered_by=self.user,
        )
        PayoutLedgerService.post_writer_payout(
            website=self.website,
            amount=Decimal("700.00"),
            writer_reference="writer_a",
            payout_id="payout_a",
            triggered_by=self.user,
        )
        PayoutLedgerService.post_writer_fine(
            website=self.website,
            amount=Decimal("100.00"),
            writer_reference="writer_a",
            fine_id="fine_a",
            triggered_by=self.user,
        )

        self.assertEqual(JournalEntry.objects.count(), 3)
        self.assertEqual(JournalLine.objects.count(), 6)

        entry_types = set(
            JournalEntry.objects.values_list("entry_type", flat=True)
        )
        self.assertEqual(
            entry_types,
            {
                LedgerEntryType.WRITER_EARNING_ACCRUAL,
                LedgerEntryType.WRITER_PAYOUT,
                LedgerEntryType.WRITER_FINE,
            },
        )