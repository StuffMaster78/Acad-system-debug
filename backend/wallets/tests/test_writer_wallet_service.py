from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from wallets.constants import WalletEntryType, WalletType
from wallets.models import WalletEntry
from wallets.services import WalletService, WriterWalletService
from websites.models.websites import Website


User = get_user_model()


class WriterWalletServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Writer Wallet Site",
            domain="https://writer-wallet-service.test",
        )
        self.writer = User.objects.create_user(
            username="writer-wallet-service",
            email="writer-wallet-service@test.local",
            password="pass",
            role="writer",
            website=self.website,
        )

    def test_get_wallet_creates_writer_wallet(self):
        wallet = WriterWalletService.get_wallet(
            website=self.website,
            writer=self.writer,
        )

        self.assertEqual(wallet.wallet_type, WalletType.WRITER)
        self.assertEqual(wallet.owner_user, self.writer)
        self.assertEqual(wallet.website, self.website)

    def test_payout_reservation_moves_available_to_pending(self):
        wallet = WriterWalletService.get_wallet(
            website=self.website,
            writer=self.writer,
        )
        WalletService.credit_wallet(
            wallet=wallet,
            website=self.website,
            amount=Decimal("120.00"),
            entry_type=WalletEntryType.EARNING,
        )

        hold = WriterWalletService.reserve_for_payout(
            website=self.website,
            writer=self.writer,
            amount=Decimal("45.00"),
            reason="writer payout test",
        )

        wallet.refresh_from_db()
        self.assertEqual(hold.amount, Decimal("45.00"))
        self.assertEqual(wallet.available_balance, Decimal("75.00"))
        self.assertEqual(wallet.pending_balance, Decimal("45.00"))
        self.assertTrue(
            WalletEntry.objects.filter(
                wallet=wallet,
                entry_type=WalletEntryType.HOLD,
            ).exists()
        )
