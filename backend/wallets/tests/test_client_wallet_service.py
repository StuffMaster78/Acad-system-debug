from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from wallets.constants import WalletEntryType, WalletType
from wallets.models import WalletEntry
from wallets.services import ClientWalletService
from websites.models.websites import Website


User = get_user_model()


class ClientWalletServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Client Wallet Site",
            domain="https://client-wallet-service.test",
        )
        self.client = User.objects.create_user(
            username="client-wallet-service",
            email="client-wallet-service@test.local",
            password="pass",
            role="client",
            website=self.website,
        )

    def test_get_wallet_creates_client_wallet(self):
        wallet = ClientWalletService.get_wallet(
            website=self.website,
            client=self.client,
        )

        self.assertEqual(wallet.wallet_type, WalletType.CLIENT)
        self.assertEqual(wallet.owner_user, self.client)
        self.assertEqual(wallet.website, self.website)

    def test_split_payment_uses_available_client_balance(self):
        wallet = ClientWalletService.get_wallet(
            website=self.website,
            client=self.client,
        )
        WalletEntry.objects.create(
            website=self.website,
            wallet=wallet,
            entry_type=WalletEntryType.FUNDING,
            direction="credit",
            amount=Decimal("40.00"),
            balance_before=Decimal("0.00"),
            balance_after=Decimal("40.00"),
        )
        wallet.available_balance = Decimal("40.00")
        wallet.total_credited = Decimal("40.00")
        wallet.save(update_fields=["available_balance", "total_credited", "updated_at"])

        split = ClientWalletService.prepare_split_payment(
            website=self.website,
            client=self.client,
            total_amount=Decimal("75.00"),
        )

        self.assertEqual(split["wallet_amount"], Decimal("40.00"))
        self.assertEqual(split["gateway_amount"], Decimal("35.00"))
        self.assertFalse(split["is_fully_covered"])
