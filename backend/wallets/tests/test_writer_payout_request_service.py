from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from wallets.constants import WalletHoldStatus
from wallets.exceptions import WalletHoldError
from wallets.models import WalletEntry
from wallets.services import (
    WalletService,
    WriterPayoutRequestService,
    WriterWalletService,
)
from websites.models.websites import Website


User = get_user_model()


class WriterPayoutRequestServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Payout Site",
            domain="https://payout.test",
        )
        self.writer = User.objects.create_user(
            username="writer-payout",
            email="writer-payout@test.local",
            password="pass",
            role="writer",
            website=self.website,
        )
        self.admin = User.objects.create_user(
            username="wallet-admin",
            email="wallet-admin@test.local",
            password="pass",
            role="admin",
            website=self.website,
        )
        self.wallet = WriterWalletService.get_wallet(
            website=self.website,
            writer=self.writer,
        )
        WalletService.credit_wallet(
            wallet=self.wallet,
            website=self.website,
            amount=Decimal("500.00"),
            entry_type="earning",
        )

    def test_request_payout_reserves_writer_funds(self):
        hold = WriterPayoutRequestService.request_payout(
            website=self.website,
            writer=self.writer,
            amount=Decimal("150.00"),
            reason="Monthly payout",
        )

        self.wallet.refresh_from_db()
        self.assertEqual(hold.status, WalletHoldStatus.ACTIVE)
        self.assertEqual(hold.reference_type, WriterPayoutRequestService.REFERENCE_TYPE)
        self.assertEqual(hold.metadata["workflow_status"], "pending")
        self.assertEqual(self.wallet.available_balance, Decimal("350.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("150.00"))

    def test_reject_payout_releases_reserved_funds(self):
        hold = WriterPayoutRequestService.request_payout(
            website=self.website,
            writer=self.writer,
            amount=Decimal("125.00"),
        )

        WriterPayoutRequestService.reject_request(
            hold=hold,
            reviewed_by=self.admin,
            review_notes="Not eligible yet",
        )

        hold.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(hold.status, WalletHoldStatus.RELEASED)
        self.assertEqual(hold.metadata["workflow_status"], "rejected")
        self.assertEqual(self.wallet.available_balance, Decimal("500.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))

    def test_approve_then_process_payout_captures_reserved_funds(self):
        hold = WriterPayoutRequestService.request_payout(
            website=self.website,
            writer=self.writer,
            amount=Decimal("200.00"),
        )

        WriterPayoutRequestService.approve_request(
            hold=hold,
            reviewed_by=self.admin,
        )
        WriterPayoutRequestService.process_request(
            hold=hold,
            processed_by=self.admin,
            external_reference="WIRE-123",
        )

        hold.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(hold.status, WalletHoldStatus.CAPTURED)
        self.assertEqual(hold.metadata["workflow_status"], "processed")
        self.assertEqual(hold.metadata["external_reference"], "WIRE-123")
        self.assertEqual(self.wallet.available_balance, Decimal("300.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))
        self.assertTrue(
            WalletEntry.objects.filter(
                wallet=self.wallet,
                reference_type=WriterPayoutRequestService.REFERENCE_TYPE,
            ).exists()
        )

    def test_writer_cannot_open_multiple_active_payout_requests(self):
        WriterPayoutRequestService.request_payout(
            website=self.website,
            writer=self.writer,
            amount=Decimal("50.00"),
        )

        with self.assertRaises(WalletHoldError):
            WriterPayoutRequestService.request_payout(
                website=self.website,
                writer=self.writer,
                amount=Decimal("25.00"),
            )
