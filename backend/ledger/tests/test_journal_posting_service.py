from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    JournalEntryStatus,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.exceptions import LedgerPostingError
from ledger.models import JournalEntry, JournalLine, LedgerAccount
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from users.models import User
from websites.models.websites import Website


class JournalPostingServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            website=self.website,
        )

        self.cash_account = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            is_system_account=True,
        )
        self.wallet_liability_account = LedgerAccount.objects.create(
            website=self.website,
            code="CLIENT_WALLET_LIABILITY",
            name="Client Wallet Liability",
            account_type=LedgerAccountType.LIABILITY,
            currency="KES",
            is_system_account=True,
        )

    def test_post_entry_creates_posted_journal_entry(self) -> None:
        entry = JournalPostingService.post_entry(
            website=self.website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            currency="KES",
            description="Wallet top up",
            triggered_by=self.user,
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
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertIsNotNone(entry.posted_at)
        self.assertEqual(
            JournalLine.objects.filter(journal_entry=entry).count(),
            2,
        )

    def test_post_entry_rejects_unbalanced_lines(self) -> None:
        with self.assertRaises(LedgerPostingError):
            JournalPostingService.post_entry(
                website=self.website,
                entry_type=LedgerEntryType.WALLET_TOP_UP,
                currency="KES",
                lines=[
                    JournalLineInput(
                        ledger_account=self.cash_account,
                        entry_side=EntrySide.DEBIT,
                        amount=Decimal("1000.00"),
                    ),
                    JournalLineInput(
                        ledger_account=self.wallet_liability_account,
                        entry_side=EntrySide.CREDIT,
                        amount=Decimal("900.00"),
                    ),
                ],
            )

        self.assertEqual(JournalEntry.objects.count(), 0)
        self.assertEqual(JournalLine.objects.count(), 0)

    def test_post_entry_rejects_zero_or_negative_amounts(self) -> None:
        with self.assertRaises(LedgerPostingError):
            JournalPostingService.post_entry(
                website=self.website,
                entry_type=LedgerEntryType.WALLET_TOP_UP,
                currency="KES",
                lines=[
                    JournalLineInput(
                        ledger_account=self.cash_account,
                        entry_side=EntrySide.DEBIT,
                        amount=Decimal("0.00"),
                    ),
                    JournalLineInput(
                        ledger_account=self.wallet_liability_account,
                        entry_side=EntrySide.CREDIT,
                        amount=Decimal("0.00"),
                    ),
                ],
            )

    def test_post_entry_rejects_cross_tenant_accounts(self) -> None:
        other_website = Website.objects.create(
            name="Other Website",
            domain="other.com",
        )
        foreign_account = LedgerAccount.objects.create(
            website=other_website,
            code="FOREIGN_CASH",
            name="Foreign Cash",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            is_system_account=True,
        )

        with self.assertRaises(LedgerPostingError):
            JournalPostingService.post_entry(
                website=self.website,
                entry_type=LedgerEntryType.WALLET_TOP_UP,
                currency="KES",
                lines=[
                    JournalLineInput(
                        ledger_account=foreign_account,
                        entry_side=EntrySide.DEBIT,
                        amount=Decimal("500.00"),
                    ),
                    JournalLineInput(
                        ledger_account=self.wallet_liability_account,
                        entry_side=EntrySide.CREDIT,
                        amount=Decimal("500.00"),
                    ),
                ],
            )

    def test_post_entry_rejects_currency_mismatch(self) -> None:
        usd_account = LedgerAccount.objects.create(
            website=self.website,
            code="USD_ACCOUNT",
            name="USD Account",
            account_type=LedgerAccountType.ASSET,
            currency="USD",
            is_system_account=True,
        )

        with self.assertRaises(LedgerPostingError):
            JournalPostingService.post_entry(
                website=self.website,
                entry_type=LedgerEntryType.WALLET_TOP_UP,
                currency="KES",
                lines=[
                    JournalLineInput(
                        ledger_account=usd_account,
                        entry_side=EntrySide.DEBIT,
                        amount=Decimal("100.00"),
                    ),
                    JournalLineInput(
                        ledger_account=self.wallet_liability_account,
                        entry_side=EntrySide.CREDIT,
                        amount=Decimal("100.00"),
                    ),
                ],
            )