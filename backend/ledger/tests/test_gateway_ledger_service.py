from decimal import Decimal

from django.test import TestCase

from ledger.constants import (
    EntrySide,
    JournalEntryStatus,
    LedgerAccountType,
    LedgerEntryType,
)
from ledger.models import JournalEntry, JournalLine, LedgerAccount
from ledger.services.gateway_ledger_service import GatewayLedgerService
from users.models import User
from websites.models.websites import Website


class GatewayLedgerServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="gatewaytester",
            email="gateway@example.com",
            password="password123",
            website=self.website,
        )

        self.gateway_clearing = LedgerAccount.objects.create(
            website=self.website,
            code="GATEWAY_CLEARING",
            name="Gateway Clearing",
            account_type=LedgerAccountType.CLEARING,
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
        self.refund_reserve = LedgerAccount.objects.create(
            website=self.website,
            code="REFUND_RESERVE",
            name="Refund Reserve",
            account_type=LedgerAccountType.LIABILITY,
            currency="USD",
            is_system_account=True,
        )

    def test_post_external_payment_capture_creates_posted_entry(self) -> None:
        entry = GatewayLedgerService.post_external_payment_capture(
            website=self.website,
            amount=Decimal("2500.00"),
            payment_intent_reference="pi_ext_1",
            external_reference="ext_txn_1",
            related_object_type="Order",
            related_object_id="123",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(
            entry.entry_type,
            LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
        )
        self.assertEqual(entry.external_reference, "ext_txn_1")
        self.assertEqual(entry.payment_intent_reference, "pi_ext_1")
        self.assertEqual(entry.source_model, "Order")
        self.assertEqual(entry.source_object_id, "123")

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
        self.assertEqual(credit_line.ledger_account, self.platform_cash)
        self.assertEqual(debit_line.amount, Decimal("2500.00"))
        self.assertEqual(credit_line.amount, Decimal("2500.00"))
        self.assertEqual(debit_line.related_object_type, "Order")
        self.assertEqual(credit_line.related_object_type, "Order")
        self.assertEqual(debit_line.related_object_id, "123")
        self.assertEqual(credit_line.related_object_id, "123")

    def test_post_external_refund_creates_posted_entry(self) -> None:
        entry = GatewayLedgerService.post_external_refund(
            website=self.website,
            amount=Decimal("900.00"),
            refund_id="refund_1",
            payment_intent_reference="pi_refund_1",
            external_reference="ext_refund_1",
            triggered_by=self.user,
        )

        self.assertEqual(entry.status, JournalEntryStatus.POSTED)
        self.assertEqual(entry.entry_type, LedgerEntryType.REFUND_EXTERNAL)
        self.assertEqual(entry.external_reference, "ext_refund_1")
        self.assertEqual(entry.payment_intent_reference, "pi_refund_1")
        self.assertEqual(entry.source_model, "Refund")
        self.assertEqual(entry.source_object_id, "refund_1")

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
        self.assertEqual(credit_line.ledger_account, self.gateway_clearing)
        self.assertEqual(debit_line.amount, Decimal("900.00"))
        self.assertEqual(credit_line.amount, Decimal("900.00"))
        self.assertEqual(debit_line.related_object_type, "Refund")
        self.assertEqual(credit_line.related_object_type, "Refund")
        self.assertEqual(debit_line.related_object_id, "refund_1")
        self.assertEqual(credit_line.related_object_id, "refund_1")

    def test_gateway_service_creates_expected_entry_count(self) -> None:
        GatewayLedgerService.post_external_payment_capture(
            website=self.website,
            amount=Decimal("1000.00"),
            payment_intent_reference="pi_1",
            external_reference="ext_1",
            related_object_type="Order",
            related_object_id="1",
            triggered_by=self.user,
        )
        GatewayLedgerService.post_external_refund(
            website=self.website,
            amount=Decimal("400.00"),
            refund_id="refund_2",
            payment_intent_reference="pi_2",
            external_reference="ext_2",
            triggered_by=self.user,
        )

        self.assertEqual(JournalEntry.objects.count(), 2)
        self.assertEqual(JournalLine.objects.count(), 4)

        entry_types = set(
            JournalEntry.objects.values_list("entry_type", flat=True)
        )
        self.assertEqual(
            entry_types,
            {
                LedgerEntryType.EXTERNAL_PAYMENT_CAPTURE,
                LedgerEntryType.REFUND_EXTERNAL,
            },
        )