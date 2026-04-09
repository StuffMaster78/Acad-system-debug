from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ledger.constants import (
    EntrySide,
    HoldStatus,
    JournalEntryStatus,
    LedgerAccountStatus,
    LedgerAccountType,
    LedgerEntryType,
    ReconciliationStatus,
)
from ledger.models import (
    HoldRecord,
    JournalEntry,
    JournalLine,
    LedgerAccount,
    ReconciliationRecord,
)
from users.models import User
from websites.models.websites import Website


class LedgerAccountModelTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Ledger Test Site",
            domain="ledger.example.com",
        )

    def test_ledger_account_str(self) -> None:
        account = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            status=LedgerAccountStatus.ACTIVE,
        )

        self.assertEqual(str(account), "PLATFORM_CASH | Platform Cash")

    def test_ledger_account_is_active_property(self) -> None:
        active_account = LedgerAccount.objects.create(
            website=self.website,
            code="ACTIVE_ACC",
            name="Active Account",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            status=LedgerAccountStatus.ACTIVE,
        )
        archived_account = LedgerAccount.objects.create(
            website=self.website,
            code="ARCHIVED_ACC",
            name="Archived Account",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            status=LedgerAccountStatus.ARCHIVED,
        )

        self.assertTrue(active_account.is_active)
        self.assertFalse(archived_account.is_active)

    def test_ledger_account_code_is_unique_per_website(self) -> None:
        LedgerAccount.objects.create(
            website=self.website,
            code="UNIQUE_CODE",
            name="First Account",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
        )

        with self.assertRaises(Exception):
            LedgerAccount.objects.create(
                website=self.website,
                code="UNIQUE_CODE",
                name="Second Account",
                account_type=LedgerAccountType.ASSET,
                currency="KES",
            )


class JournalEntryModelTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Journal Site",
            domain="journal.example.com",
        )
        self.user = User.objects.create_user(
            username="journaltester",
            email="journal@example.com",
            password="password123",
            website=self.website,
        )

    def test_journal_entry_str(self) -> None:
        entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-001",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.DRAFT,
            currency="KES",
        )

        self.assertEqual(str(entry), "JE-001 | draft")

    def test_journal_entry_mark_posted_sets_status_and_posted_at(self) -> None:
        entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-002",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.DRAFT,
            currency="KES",
        )

        entry.mark_posted()

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertIsNotNone(entry.posted_at)

    def test_journal_entry_mark_reversed_sets_status(self) -> None:
        entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-003",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.POSTED,
            currency="KES",
            posted_at=timezone.now(),
        )

        entry.mark_reversed()

        self.assertEqual(entry.status, JournalEntryStatus.REVERSED)

    def test_journal_entry_clean_rejects_posted_without_posted_at(self) -> None:
        entry = JournalEntry(
            website=self.website,
            entry_number="JE-004",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.POSTED,
            currency="KES",
            posted_at=None,
        )

        with self.assertRaises(ValidationError):
            entry.clean()

    def test_journal_entry_clean_accepts_posted_with_posted_at(self) -> None:
        entry = JournalEntry(
            website=self.website,
            entry_number="JE-005",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.POSTED,
            currency="KES",
            posted_at=timezone.now(),
        )

        entry.clean()

    def test_journal_entry_properties(self) -> None:
        draft_entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-006",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.DRAFT,
            currency="KES",
        )
        posted_entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-007",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.POSTED,
            currency="KES",
            posted_at=timezone.now(),
        )
        reversed_entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-008",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.REVERSED,
            currency="KES",
        )

        self.assertTrue(draft_entry.is_draft)
        self.assertFalse(draft_entry.is_posted)
        self.assertTrue(posted_entry.is_posted)
        self.assertFalse(posted_entry.is_reversed)
        self.assertTrue(reversed_entry.is_reversed)


class JournalLineModelTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Line Site",
            domain="line.example.com",
        )
        self.other_website = Website.objects.create(
            name="Other Site",
            domain="other-line.example.com",
        )
        self.user = User.objects.create_user(
            username="linetester",
            email="line@example.com",
            password="password123",
            website=self.website,
        )
        self.entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-LINE-001",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.DRAFT,
            currency="KES",
        )
        self.account = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
        )

    def test_journal_line_str(self) -> None:
        line = JournalLine.objects.create(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.DEBIT,
            amount=Decimal("100.00"),
            currency="KES",
        )

        self.assertEqual(str(line), "debit | 100.00")

    def test_journal_line_clean_rejects_non_positive_amount(self) -> None:
        line = JournalLine(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.DEBIT,
            amount=Decimal("0.00"),
            currency="KES",
        )

        with self.assertRaises(ValidationError):
            line.clean()

    def test_journal_line_clean_rejects_invalid_entry_side(self) -> None:
        line = JournalLine(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side="sideways",
            amount=Decimal("100.00"),
            currency="KES",
        )

        with self.assertRaises(ValidationError):
            line.clean()

    def test_journal_line_clean_rejects_currency_mismatch(self) -> None:
        line = JournalLine(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.DEBIT,
            amount=Decimal("100.00"),
            currency="USD",
        )

        with self.assertRaises(ValidationError):
            line.clean()

    def test_journal_line_clean_rejects_tenant_mismatch(self) -> None:
        line = JournalLine(
            website=self.other_website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.DEBIT,
            amount=Decimal("100.00"),
            currency="KES",
        )

        with self.assertRaises(ValidationError):
            line.clean()

    def test_journal_line_properties(self) -> None:
        debit_line = JournalLine.objects.create(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.DEBIT,
            amount=Decimal("50.00"),
            currency="KES",
        )
        credit_line = JournalLine.objects.create(
            website=self.website,
            journal_entry=self.entry,
            ledger_account=self.account,
            entry_side=EntrySide.CREDIT,
            amount=Decimal("50.00"),
            currency="KES",
        )

        self.assertTrue(debit_line.is_debit)
        self.assertFalse(debit_line.is_credit)
        self.assertTrue(credit_line.is_credit)
        self.assertFalse(credit_line.is_debit)


class HoldRecordModelTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Hold Site",
            domain="hold.example.com",
        )
        self.user = User.objects.create_user(
            username="holdtester",
            email="hold@example.com",
            password="password123",
            website=self.website,
        )
        self.account = LedgerAccount.objects.create(
            website=self.website,
            code="CLIENT_WALLET_LIABILITY",
            name="Client Wallet Liability",
            account_type=LedgerAccountType.LIABILITY,
            currency="KES",
        )

    def test_hold_record_status_properties(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("500.00"),
            currency="KES",
            status=HoldStatus.ACTIVE,
        )

        self.assertTrue(hold.is_active)
        self.assertFalse(hold.is_final)

        hold.status = HoldStatus.RELEASED
        self.assertTrue(hold.is_released)
        self.assertTrue(hold.is_final)

    def test_hold_record_mark_captured(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("400.00"),
            currency="KES",
            status=HoldStatus.ACTIVE,
        )

        hold.mark_captured()

        self.assertEqual(hold.status, HoldStatus.CAPTURED)
        self.assertIsNotNone(hold.captured_at)

    def test_hold_record_mark_released(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("400.00"),
            currency="KES",
            status=HoldStatus.ACTIVE,
        )

        hold.mark_released()

        self.assertEqual(hold.status, HoldStatus.RELEASED)
        self.assertIsNotNone(hold.released_at)

    def test_hold_record_clean_rejects_non_positive_amount(self) -> None:
        hold = HoldRecord(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("0.00"),
            currency="KES",
            status=HoldStatus.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            hold.clean()


class ReconciliationRecordModelTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Recon Site",
            domain="recon.example.com",
        )
        self.user = User.objects.create_user(
            username="recontester",
            email="recon@example.com",
            password="password123",
            website=self.website,
        )

    def test_reconciliation_record_status_properties(self) -> None:
        record = ReconciliationRecord.objects.create(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("1000.00"),
            matched_amount=Decimal("0.00"),
            variance_amount=Decimal("0.00"),
        )

        self.assertTrue(record.is_unreconciled)
        self.assertFalse(record.is_final)

        record.status = ReconciliationStatus.MATCHED
        self.assertTrue(record.is_matched)
        self.assertTrue(record.is_final)

    def test_mark_matched_updates_fields(self) -> None:
        record = ReconciliationRecord.objects.create(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("1000.00"),
            matched_amount=Decimal("0.00"),
            variance_amount=Decimal("0.00"),
        )

        record.mark_matched(Decimal("1000.00"))

        self.assertEqual(record.status, ReconciliationStatus.MATCHED)
        self.assertEqual(record.actual_amount, Decimal("1000.00"))
        self.assertEqual(record.matched_amount, Decimal("1000.00"))
        self.assertEqual(record.variance_amount, Decimal("0.00"))
        self.assertIsNotNone(record.reconciled_at)

    def test_mark_mismatched_updates_fields(self) -> None:
        record = ReconciliationRecord.objects.create(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("1000.00"),
            actual_amount=Decimal("700.00"),
            matched_amount=Decimal("0.00"),
            variance_amount=Decimal("0.00"),
        )

        record.mark_mismatched("Amount mismatch")

        self.assertEqual(record.status, ReconciliationStatus.MISMATCHED)
        self.assertEqual(record.mismatch_reason, "Amount mismatch")
        self.assertEqual(record.variance_amount, Decimal("300.00"))

    def test_mark_resolved_sets_status_and_time(self) -> None:
        record = ReconciliationRecord.objects.create(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.MISMATCHED,
            currency="KES",
            expected_amount=Decimal("1000.00"),
            actual_amount=Decimal("800.00"),
            matched_amount=Decimal("800.00"),
            variance_amount=Decimal("200.00"),
        )

        record.mark_resolved(resolved_by=self.user)

        self.assertEqual(record.status, ReconciliationStatus.RESOLVED)
        self.assertEqual(record.resolved_by, self.user)
        self.assertIsNotNone(record.resolved_at)

    def test_clean_rejects_non_positive_expected_amount(self) -> None:
        record = ReconciliationRecord(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("0.00"),
            matched_amount=Decimal("0.00"),
            variance_amount=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_clean_rejects_negative_actual_amount(self) -> None:
        record = ReconciliationRecord(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("100.00"),
            actual_amount=Decimal("-1.00"),
            matched_amount=Decimal("0.00"),
            variance_amount=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_clean_rejects_negative_matched_amount(self) -> None:
        record = ReconciliationRecord(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.UNRECONCILED,
            currency="KES",
            expected_amount=Decimal("100.00"),
            matched_amount=Decimal("-1.00"),
            variance_amount=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_clean_requires_resolved_at_for_resolved_status(self) -> None:
        record = ReconciliationRecord(
            website=self.website,
            user=self.user,
            status=ReconciliationStatus.RESOLVED,
            currency="KES",
            expected_amount=Decimal("100.00"),
            matched_amount=Decimal("100.00"),
            variance_amount=Decimal("0.00"),
            resolved_at=None,
        )

        with self.assertRaises(ValidationError):
            record.clean()