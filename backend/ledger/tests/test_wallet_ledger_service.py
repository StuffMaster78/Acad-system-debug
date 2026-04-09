from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    JournalEntryStatus,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.models import JournalEntry, JournalLine, LedgerAccount
from ledger.services.wallet_ledger_service import WalletLedgerService
from users.models import User
from websites.models.websites import Website


class WalletLedgerServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="wallettester",
            email="wallet@example.com",
            password="password123",
            website=self.website,
        )

        self.gateway_clearing = LedgerAccount.objects.create(
            website=self.website,
            code="GATEWAY_CLEARING",
            name="Gateway Clearing",
            account_type=LedgerAccountType.CLEARING,
            currency="KES",
            is_system_account=True,
        )
        self.client_wallet_liability = LedgerAccount.objects.create(
            website=self.website,
            code="CLIENT_WALLET_LIABILITY",
            name="Client Wallet Liability",
            account_type=LedgerAccountType.LIABILITY,
            currency="KES",
            is_system_account=True,
        )
        self.platform_cash = LedgerAccount.objects.create(
            website=self.website,
            code="PLATFORM_CASH",
            name="Platform Cash",
            account_type=LedgerAccountType.ASSET,
            currency="KES",
            is_system_account=True,
        )
        self.refund_reserve = LedgerAccount.objects.create(
            website=self.website,
            code="REFUND_RESERVE",
            name="Refund Reserve",
            account_type=LedgerAccountType.LIABILITY,
            currency="KES",
            is_system_account=True,
        )

    def test_post_wallet_top_up_creates_posted_entry(self) -> None:
        entry = WalletLedgerService.post_wallet_top_up(
            website=self.website,
            amount=Decimal("1000.00"),
            wallet_reference="wallet_1",
            payment_intent_reference="pi_123",
            external_reference="ext_123",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.WALLET_TOP_UP)
        self.assertEqual(entry.external_reference, "ext_123")
        self.assertEqual(entry.payment_intent_reference, "pi_123")

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

        self.assertEqual(debit_line.ledger_account, self.gateway_clearing)
        self.assertEqual(credit_line.ledger_account, self.client_wallet_liability)
        self.assertEqual(debit_line.amount, Decimal("1000.00"))
        self.assertEqual(credit_line.amount, Decimal("1000.00"))
        self.assertEqual(debit_line.wallet_reference, "wallet_1")
        self.assertEqual(credit_line.wallet_reference, "wallet_1")

    def test_post_wallet_debit_for_order_creates_posted_entry(self) -> None:
        entry = WalletLedgerService.post_wallet_debit_for_order(
            website=self.website,
            amount=Decimal("500.00"),
            wallet_reference="wallet_2",
            order_id="42",
            payment_intent_reference="pi_order_42",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.WALLET_DEBIT)
        self.assertEqual(entry.source_model, "Order")
        self.assertEqual(entry.source_object_id, "42")
        self.assertEqual(entry.payment_intent_reference, "pi_order_42")

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

        self.assertEqual(
            debit_line.ledger_account,
            self.client_wallet_liability,
        )
        self.assertEqual(credit_line.ledger_account, self.platform_cash)
        self.assertEqual(debit_line.related_object_type, "Order")
        self.assertEqual(credit_line.related_object_type, "Order")
        self.assertEqual(debit_line.related_object_id, "42")
        self.assertEqual(credit_line.related_object_id, "42")
        self.assertEqual(debit_line.wallet_reference, "wallet_2")
        self.assertEqual(credit_line.wallet_reference, "wallet_2")

    def test_post_wallet_refund_creates_posted_entry(self) -> None:
        entry = WalletLedgerService.post_wallet_refund(
            website=self.website,
            amount=Decimal("750.00"),
            wallet_reference="wallet_3",
            refund_id="refund_55",
            payment_intent_reference="pi_refund_55",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.REFUND_TO_WALLET)
        self.assertEqual(entry.source_model, "Refund")
        self.assertEqual(entry.source_object_id, "refund_55")

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

        self.assertEqual(debit_line.ledger_account, self.refund_reserve)
        self.assertEqual(credit_line.ledger_account, self.client_wallet_liability)
        self.assertEqual(debit_line.related_object_type, "Refund")
        self.assertEqual(credit_line.related_object_type, "Refund")
        self.assertEqual(debit_line.related_object_id, "refund_55")
        self.assertEqual(credit_line.related_object_id, "refund_55")
        self.assertEqual(debit_line.wallet_reference, "wallet_3")
        self.assertEqual(credit_line.wallet_reference, "wallet_3")

    def test_post_wallet_top_up_creates_balanced_lines(self) -> None:
        entry = WalletLedgerService.post_wallet_top_up(
            website=self.website,
            amount=Decimal("1200.00"),
            wallet_reference="wallet_balance",
            triggered_by=self.user,
        )

        debit_total = (
            JournalLine.objects.filter(
                journal_entry=entry,
                entry_side=EntrySide.DEBIT,
            )
            .values_list("amount", flat=True)
            .first()
        )
        credit_total = (
            JournalLine.objects.filter(
                journal_entry=entry,
                entry_side=EntrySide.CREDIT,
            )
            .values_list("amount", flat=True)
            .first()
        )

        self.assertEqual(debit_total, Decimal("1200.00"))
        self.assertEqual(credit_total, Decimal("1200.00"))

    def test_post_wallet_entries_create_expected_journal_entries(self) -> None:
        WalletLedgerService.post_wallet_top_up(
            website=self.website,
            amount=Decimal("300.00"),
            wallet_reference="wallet_a",
            triggered_by=self.user,
        )
        WalletLedgerService.post_wallet_debit_for_order(
            website=self.website,
            amount=Decimal("200.00"),
            wallet_reference="wallet_a",
            order_id="101",
            triggered_by=self.user,
        )
        WalletLedgerService.post_wallet_refund(
            website=self.website,
            amount=Decimal("100.00"),
            wallet_reference="wallet_a",
            refund_id="ref_101",
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
                LedgerEntryType.WALLET_TOP_UP,
                LedgerEntryType.WALLET_DEBIT,
                LedgerEntryType.REFUND_TO_WALLET,
            },
        )