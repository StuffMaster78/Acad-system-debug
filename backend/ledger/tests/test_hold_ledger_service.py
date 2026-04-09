from decimal import Decimal

from django.test import TestCase

from ledger.constants import HoldStatus, LedgerAccountType
from ledger.exceptions import LedgerHoldError
from ledger.models import HoldRecord, LedgerAccount
from ledger.services.hold_ledger_service import HoldLedgerService
from users.models import User
from websites.models.websites import Website


class HoldLedgerServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Test Website",
            domain="example.com",
        )
        self.user = User.objects.create_user(
            username="testuser",
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
            is_system_account=True,
        )

    def test_create_hold_creates_active_hold(self) -> None:
        hold = HoldLedgerService.create_hold(
            website=self.website,
            ledger_account=self.account,
            amount=Decimal("2500.00"),
            user=self.user,
            wallet_reference="wallet_1",
            payment_intent_reference="pi_123",
        )

        self.assertEqual(hold.status, HoldStatus.ACTIVE)
        self.assertEqual(hold.amount, Decimal("2500.00"))

    def test_create_hold_rejects_non_positive_amount(self) -> None:
        with self.assertRaises(LedgerHoldError):
            HoldLedgerService.create_hold(
                website=self.website,
                ledger_account=self.account,
                amount=Decimal("0.00"),
            )

    def test_release_hold_updates_status(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("300.00"),
            currency="KES",
        )

        released_hold = HoldLedgerService.release_hold(hold=hold)

        self.assertEqual(released_hold.status, HoldStatus.RELEASED)
        self.assertIsNotNone(released_hold.released_at)

    def test_capture_hold_updates_status(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("300.00"),
            currency="KES",
        )

        captured_hold = HoldLedgerService.capture_hold(hold=hold)

        self.assertEqual(captured_hold.status, HoldStatus.CAPTURED)
        self.assertIsNotNone(captured_hold.captured_at)

    def test_release_non_active_hold_raises_error(self) -> None:
        hold = HoldRecord.objects.create(
            website=self.website,
            ledger_account=self.account,
            user=self.user,
            amount=Decimal("300.00"),
            currency="KES",
            status=HoldStatus.RELEASED,
        )

        with self.assertRaises(LedgerHoldError):
            HoldLedgerService.release_hold(hold=hold)