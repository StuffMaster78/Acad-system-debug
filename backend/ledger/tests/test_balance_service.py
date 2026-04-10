from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.models import LedgerAccount
from ledger.services.balance_service import BalanceService
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from websites.models.websites import Website


class BalanceServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
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

    def test_get_account_balance_for_asset_account(self) -> None:
        JournalPostingService.post_entry(
            website=self.website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            lines=[
                JournalLineInput(
                    ledger_account=self.cash_account,
                    entry_side=EntrySide.DEBIT,
                    amount=Decimal("1500.00"),
                ),
                JournalLineInput(
                    ledger_account=self.wallet_liability_account,
                    entry_side=EntrySide.CREDIT,
                    amount=Decimal("1500.00"),
                ),
            ],
        )

        balance = BalanceService.get_account_balance(
            account=self.cash_account,
        )

        self.assertEqual(balance, Decimal("1500.00"))

    def test_get_account_balance_for_liability_account(self) -> None:
        JournalPostingService.post_entry(
            website=self.website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            lines=[
                JournalLineInput(
                    ledger_account=self.cash_account,
                    entry_side=EntrySide.DEBIT,
                    amount=Decimal("2000.00"),
                ),
                JournalLineInput(
                    ledger_account=self.wallet_liability_account,
                    entry_side=EntrySide.CREDIT,
                    amount=Decimal("2000.00"),
                ),
            ],
        )

        balance = BalanceService.get_account_balance(
            account=self.wallet_liability_account,
        )

        self.assertEqual(balance, Decimal("2000.00"))

    def test_create_snapshot_uses_current_balance(self) -> None:
        JournalPostingService.post_entry(
            website=self.website,
            entry_type=LedgerEntryType.WALLET_TOP_UP,
            lines=[
                JournalLineInput(
                    ledger_account=self.cash_account,
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

        snapshot = BalanceService.create_snapshot(
            account=self.cash_account,
            reference="daily_close",
        )

        self.assertEqual(snapshot.balance, Decimal("500.00"))
        self.assertEqual(snapshot.reference, "daily_close")