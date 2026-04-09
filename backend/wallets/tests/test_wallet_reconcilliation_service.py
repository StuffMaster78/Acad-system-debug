from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from wallets.models import Wallet
from wallets.services import (
    WalletService,
    WalletHoldService,
    WalletReconciliationService,
)

User = get_user_model()


class WalletReconciliationServiceTests(TestCase):
    def setUp(self):
        self.website = self._create_website()

        self.user = User.objects.create_user(
            username="Test Name",
            email="user@test.com",
            password="testpass",
        )
        self.user.website = self.website
        self.user.save()

        self.wallet = WalletService.get_client_wallet(
            website=self.website,
            owner_user=self.user,
        )

        WalletService.credit_wallet(
            wallet=self.wallet,
            amount=Decimal("1000.00"),
            entry_type="funding",
            website=self.website,
        )

    def _create_website(self):
        from websites.models import Website
        return Website.objects.create(name="Test Site")

    def test_reconciliation_clean_wallet(self):
        result = WalletReconciliationService.reconcile_wallet(
            wallet=self.wallet
        )

        self.assertTrue(result.available_balance_matches)
        self.assertTrue(result.pending_balance_matches)
        self.assertTrue(result.entry_chain_is_consistent)

    def test_reconciliation_with_hold(self):
        WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("300.00"),
            website=self.website,
            reason="Hold test",
        )

        self.wallet.refresh_from_db()

        result = WalletReconciliationService.reconcile_wallet(
            wallet=self.wallet
        )

        self.assertTrue(result.pending_balance_matches)
        self.assertTrue(result.available_balance_matches)

    def test_detect_available_balance_drift(self):
        # break balance manually
        self.wallet.available_balance = Decimal("9999.00")
        self.wallet.save()

        result = WalletReconciliationService.reconcile_wallet(
            wallet=self.wallet
        )

        self.assertFalse(result.available_balance_matches)

    def test_detect_pending_balance_drift(self):
        WalletHoldService.create_hold(
            wallet=self.wallet,
            amount=Decimal("200.00"),
            website=self.website,
            reason="Hold drift",
        )

        self.wallet.pending_balance = Decimal("9999.00")
        self.wallet.save()

        result = WalletReconciliationService.reconcile_wallet(
            wallet=self.wallet
        )

        self.assertFalse(result.pending_balance_matches)

    def test_repair_wallet(self):
        self.wallet.available_balance = Decimal("9999.00")
        self.wallet.pending_balance = Decimal("8888.00")
        self.wallet.save()

        repaired = WalletReconciliationService.repair_wallet_balances(
            wallet=self.wallet,
        )

        self.wallet.refresh_from_db()

        self.assertTrue(repaired.available_balance_matches)
        self.assertTrue(repaired.pending_balance_matches)

    def test_entry_chain_validation(self):
        WalletService.debit_wallet(
            wallet=self.wallet,
            amount=Decimal("100.00"),
            entry_type="order_payment",
            website=self.website,
        )

        result = WalletReconciliationService.reconcile_wallet(
            wallet=self.wallet
        )

        self.assertTrue(result.entry_chain_is_consistent)