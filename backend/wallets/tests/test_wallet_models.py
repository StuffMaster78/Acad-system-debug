from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from wallets.constants import WalletType
from wallets.models import Wallet
from websites.models.websites import Website


User = get_user_model()


class WalletModelTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Wallet Model Site",
            domain="https://wallet-model.test",
        )
        self.user = User.objects.create_user(
            username="wallet-model-user",
            email="wallet-model@test.local",
            password="pass",
            website=self.website,
        )

    def test_wallet_is_unique_per_owner_type_currency_and_website(self):
        Wallet.objects.create(
            website=self.website,
            owner_user=self.user,
            wallet_type=WalletType.CLIENT,
            currency="USD",
        )

        with self.assertRaises(Exception):
            Wallet.objects.create(
                website=self.website,
                owner_user=self.user,
                wallet_type=WalletType.CLIENT,
                currency="USD",
            )

    def test_wallet_rejects_negative_cached_balances(self):
        wallet = Wallet(
            website=self.website,
            owner_user=self.user,
            wallet_type=WalletType.CLIENT,
            available_balance=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            wallet.clean()
