from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch

from wallet.exceptions import InsufficientWalletBalance
from wallet.services.wallet_transaction_service import WalletTransactionService
from wallets.constants import WalletEntryType, WalletType
from wallets.models import Wallet, WalletEntry
from websites.models.websites import Website


User = get_user_model()


class LegacyWalletTransactionServiceTests(TestCase):
    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Wallet Site",
            domain="https://wallet.test",
        )
        self.client = User.objects.create_user(
            email="client-wallet@test.local",
            username="client-wallet",
            password="pass",
            role="client",
            website=self.website,
        )

    @patch("notifications_system.services.notification_service.NotificationService.notify")
    def test_credit_and_debit_are_recorded_in_wallets_app(self, _mock_notify):
        credit = WalletTransactionService.credit(
            user=self.client,
            website=self.website,
            amount=Decimal("25.00"),
            transaction_type="referral_bonus",
            source="referral",
        )
        debit = WalletTransactionService.debit(
            user=self.client,
            website=self.website,
            amount=Decimal("10.00"),
            transaction_type="loyalty_conversion",
            source="loyalty",
        )

        wallet = Wallet.objects.get(
            website=self.website,
            owner_user=self.client,
            wallet_type=WalletType.CLIENT,
        )
        self.assertEqual(wallet.available_balance, Decimal("15.00"))
        self.assertEqual(credit.entry_type, WalletEntryType.REFERRAL_BONUS)
        self.assertEqual(debit.entry_type, WalletEntryType.LOYALTY_CONVERSION)
        self.assertEqual(WalletEntry.objects.filter(wallet=wallet).count(), 2)

    def test_debit_rejects_insufficient_balance(self):
        with self.assertRaises(InsufficientWalletBalance):
            WalletTransactionService.debit(
                user=self.client,
                website=self.website,
                amount=Decimal("10.00"),
            )
