from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from wallets.constants import WalletEntryType, WalletType
from wallets.selectors import (
    WalletEntrySelectors,
    WalletHoldSelectors,
    WalletSelectors,
)
from wallets.services import WalletHoldService, WalletService
from websites.models.websites import Website


User = get_user_model()


class WalletSelectorTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Selector Site",
            domain="https://wallet-selectors.test",
        )
        self.client = User.objects.create_user(
            username="selector-client",
            email="selector-client@test.local",
            password="pass",
            role="client",
            website=self.website,
        )
        self.writer = User.objects.create_user(
            username="selector-writer",
            email="selector-writer@test.local",
            password="pass",
            role="writer",
            website=self.website,
        )

    def test_owner_wallets_and_entries_are_tenant_scoped(self):
        client_wallet = WalletService.get_client_wallet(
            website=self.website,
            owner_user=self.client,
        )
        writer_wallet = WalletService.get_writer_wallet(
            website=self.website,
            owner_user=self.writer,
        )

        WalletService.credit_wallet(
            wallet=client_wallet,
            website=self.website,
            amount=Decimal("80.00"),
            entry_type=WalletEntryType.FUNDING,
        )
        WalletService.credit_wallet(
            wallet=writer_wallet,
            website=self.website,
            amount=Decimal("35.00"),
            entry_type=WalletEntryType.EARNING,
        )

        balances = WalletSelectors.balances_for_owner(
            website=self.website,
            owner_user=self.client,
        )

        self.assertEqual(balances[WalletType.CLIENT], Decimal("80.00"))
        self.assertEqual(
            WalletEntrySelectors.for_owner(
                website=self.website,
                owner_user=self.client,
                wallet_type=WalletType.CLIENT,
            ).count(),
            1,
        )
        self.assertEqual(
            WalletEntrySelectors.for_owner(
                website=self.website,
                owner_user=self.client,
                wallet_type=WalletType.WRITER,
            ).count(),
            0,
        )

    def test_hold_selectors_return_active_holds_for_owner(self):
        wallet = WalletService.get_client_wallet(
            website=self.website,
            owner_user=self.client,
        )
        WalletService.credit_wallet(
            wallet=wallet,
            website=self.website,
            amount=Decimal("100.00"),
            entry_type=WalletEntryType.FUNDING,
        )

        hold = WalletHoldService.create_hold(
            wallet=wallet,
            website=self.website,
            amount=Decimal("25.00"),
            reason="selector hold",
        )

        self.assertEqual(
            WalletHoldSelectors.for_owner(
                website=self.website,
                owner_user=self.client,
                wallet_type=WalletType.CLIENT,
            ).count(),
            1,
        )
        self.assertEqual(
            WalletHoldSelectors.active_for_wallet(wallet=wallet).get(),
            hold,
        )
