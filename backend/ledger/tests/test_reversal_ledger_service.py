from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    JournalEntryStatus,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.exceptions import LedgerReversalError
from ledger.models import JournalEntry, JournalLine, LedgerAccount
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from ledger.services.reversal_ledger_service import ReversalLedgerService
from users.models import User
from websites.models.websites import Website


class ReversalLedgerServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="reverse@example.com",
            password="password123",
            website=self.website,
        )

        self.cash_account = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="USD",
            is_system_account=True,
        )
        self.wallet_liability_account = LedgerAccount.objects.create(
            website=self.website,
            code="CLIENT_WALLET_LIABILITY",
            name="Client Wallet Liability",
            account_type=LedgerAccountType.LIABILITY,
            currency="USD",
            is_system_account=True,
        )

    def test_reverse_posted_entry_creates_reversal(self) -> None:
        original_entry = JournalPostingService.post_entry(
            website=self.website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            lines=[
                JournalLineInput(
                    ledger_account=self.cash_account,
                    entry_side=EntrySide.DEBIT,
                    amount=Decimal("1000.00"),
                ),
                JournalLineInput(
                    ledger_account=self.wallet_liability_account,
                    entry_side=EntrySide.CREDIT,
                    amount=Decimal("1000.00"),
                ),
            ],
            triggered_by=self.user,
        )

        reversal_entry = ReversalLedgerService.reverse_entry(
            journal_entry=original_entry,
            triggered_by=self.user,
            reason="Manual correction",
        )

        original_entry.refresh_from_db()

        self.assertEqual(original_entry.status, JournalEntryStatus.REVERSED)
        self.assertEqual(reversal_entry.reversal_of, original_entry)
        self.assertEqual(reversal_entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(
            JournalLine.objects.filter(journal_entry=reversal_entry).count(),
            2,
        )

    def test_reverse_non_posted_entry_raises_error(self) -> None:
        draft_entry = JournalEntry.objects.create(
            website=self.website,
            entry_number="JE-DRAFT-1",
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            status=JournalEntryStatus.DRAFT,
            currency="USD",
        )

        with self.assertRaises(LedgerReversalError):
            ReversalLedgerService.reverse_entry(
                journal_entry=draft_entry,
                triggered_by=self.user,
            )