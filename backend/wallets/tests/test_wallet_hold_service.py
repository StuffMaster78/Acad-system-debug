from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from wallets.constants import WalletHoldStatus
from wallets.models import WalletHold
from wallets.services import WalletService, WalletHoldService

User = get_user_model()


class WalletHoldServiceTests(TestCase):
    def setUp(self):
        self.website = self._create_website()
        self.user = User.objects.create_user(
            username="Test User",
            email="client@test.com",
            password="testpass",
        )
        self.user.website = self.website
        self.user.save()

        self.wallet = WalletService.get_client_wallet(
            website=self.website,
            owner_user=self.user,
        )

        # Fund wallet
        WalletService.credit_wallet(
            wallet=self.wallet,
            amount=Decimal("1000.00"),
            entry_type="funding",
            website=self.website,
        )

    def _create_website(self):
        from websites.models import Website
        return Website.objects.create(name="Test Site")

    def test_create_hold(self):
        hold = WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("300.00"),
            website=self.website,
            reason="Test hold",
        )

        self.wallet.refresh_from_db()

        self.assertEqual(hold.status, WalletHoldStatus.ACTIVE)
        self.assertEqual(self.wallet.available_balance, Decimal("700.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("300.00"))

    def test_release_hold(self):
        hold = WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("200.00"),
            website=self.website,
            reason="Release test",
        )

        WalletHoldService.release_hold(hold=hold)

        self.wallet.refresh_from_db()
        hold.refresh_from_db()

        self.assertEqual(hold.status, WalletHoldStatus.RELEASED)
        self.assertEqual(self.wallet.available_balance, Decimal("1000.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))

    def test_capture_hold(self):
        hold = WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("400.00"),
            website=self.website,
            reason="Capture test",
        )

        WalletHoldService.capture_hold(hold=hold)

        self.wallet.refresh_from_db()
        hold.refresh_from_db()

        self.assertEqual(hold.status, WalletHoldStatus.CAPTURED)
        self.assertEqual(self.wallet.available_balance, Decimal("600.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))

    def test_expire_hold(self):
        hold = WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("250.00"),
            website=self.website,
            reason="Expire test",
        )

        WalletHoldService.expire_hold(hold=hold)

        self.wallet.refresh_from_db()
        hold.refresh_from_db()

        self.assertEqual(hold.status, WalletHoldStatus.EXPIRED)
        self.assertEqual(self.wallet.available_balance, Decimal("1000.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))

    def test_cannot_create_hold_with_insufficient_balance(self):
        with self.assertRaises(Exception):
            WalletHoldService.create_hold(
                wallet=self.wallet,
                amount=Decimal("2000.00"),
                website=self.website,
                reason="Too big",
            )

    def test_cannot_release_non_active_hold(self):
        hold = WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("100.00"),
            website=self.website,
            reason="Test",
        )

        WalletHoldService.capture_hold(hold=hold)

        with self.assertRaises(Exception):
            WalletHoldService.release_hold(hold=hold)