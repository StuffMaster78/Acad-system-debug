from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments_processor.enums import PaymentAllocationStatus, PaymentIntentPurpose
from payments_processor.models import PaymentAllocation
from payments_processor.services.payment_allocation_application_service import (
    PaymentAllocationApplicationService,
)
from payments_processor.services.payment_allocation_service import (
    PaymentAllocationService,
)
from wallets.constants import WalletEntryType, WalletHoldStatus
from wallets.models import WalletEntry
from wallets.services import WalletService
from websites.models.websites import Website


User = get_user_model()


class WalletAllocationApplicationTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Payments Wallet Site",
            domain="https://payments-wallet.test",
        )
        self.client = User.objects.create_user(
            username="payments-client",
            email="payments-client@test.local",
            password="pass",
            role="client",
            website=self.website,
        )
        self.wallet = WalletService.get_client_wallet(
            website=self.website,
            owner_user=self.client,
        )
        WalletService.credit_wallet(
            wallet=self.wallet,
            website=self.website,
            amount=Decimal("150.00"),
            entry_type=WalletEntryType.FUNDING,
        )

    def test_wallet_only_allocation_captures_hold_once(self):
        result = PaymentAllocationService.create_allocations_for_payable(
            client=self.client,
            payable=self.website,
            purpose=PaymentIntentPurpose.ORDER,
            total_amount=Decimal("70.00"),
        )
        allocation = result["allocations"][0]

        self.wallet.refresh_from_db()
        self.assertEqual(result["mode"], "wallet_only")
        self.assertEqual(allocation.customer, self.client)
        self.assertEqual(allocation.status, PaymentAllocationStatus.PENDING)
        self.assertEqual(allocation.wallet_hold.status, WalletHoldStatus.ACTIVE)
        self.assertEqual(self.wallet.available_balance, Decimal("80.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("70.00"))

        PaymentAllocationApplicationService.apply_wallet_only_payment(
            payable=self.website,
            total_amount=Decimal("70.00"),
        )

        allocation = PaymentAllocation.objects.get(pk=allocation.pk)
        allocation.wallet_hold.refresh_from_db()
        self.wallet.refresh_from_db()

        self.assertEqual(allocation.status, PaymentAllocationStatus.APPLIED)
        self.assertEqual(allocation.wallet_hold.status, WalletHoldStatus.CAPTURED)
        self.assertEqual(self.wallet.available_balance, Decimal("80.00"))
        self.assertEqual(self.wallet.pending_balance, Decimal("0.00"))
        self.assertEqual(
            WalletEntry.objects.filter(
                wallet=self.wallet,
                entry_type=WalletEntryType.HOLD_CAPTURE,
            ).count(),
            1,
        )
