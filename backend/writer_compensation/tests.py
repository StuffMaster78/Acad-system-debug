from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models.account_profile import AccountProfile
from wallets.constants import WalletHoldStatus, WalletType
from wallets.models import Wallet, WalletEntry, WalletHold
from websites.models.websites import Website
from writer_compensation.enums.compensation_enums import (
    PayoutRecordStatus,
    SettlementStatus,
    WindowStatus,
    WindowType,
)
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.models.payout_record import PayoutRecord
from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.services.payout_engine_service import PayoutEngineService
from writer_compensation.services.settlement_engine_service import (
    SettlementEngineService,
)
from writer_compensation.services.wallet_sync_service import (
    CompensationWalletSyncService,
)
from writer_management.models.writer_profile import WriterProfile


User = get_user_model()


class WriterCompensationWalletSyncTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Comp Site",
            domain="https://comp.test",
        )
        self.writer_user = User.objects.create_user(
            username="comp-writer",
            email="comp-writer@test.local",
            password="pass",
            role="writer",
            website=self.website,
        )
        self.admin = User.objects.create_user(
            username="comp-admin",
            email="comp-admin@test.local",
            password="pass",
            role="admin",
            website=self.website,
        )
        self.account_profile = AccountProfile.objects.create(
            website=self.website,
            user=self.writer_user,
            is_primary=True,
        )
        self.writer_profile = WriterProfile.objects.create(
            account_profile=self.account_profile,
            registration_id="WR-COMP-001",
        )
        self.window = PaymentWindow.objects.create(
            website=self.website,
            title="May Window",
            cycle_type=WindowType.MONTHLY,
            status=WindowStatus.PROCESSING,
            start_date="2026-05-01",
            end_date="2026-05-31",
        )

    def test_finalized_settlement_credits_writer_wallet_once(self):
        period = SettlementPeriod.objects.create(
            website=self.website,
            writer=self.writer_profile,
            payment_window=self.window,
            net_payable=Decimal("240.00"),
        )

        SettlementEngineService.finalize_settlement_period(
            period=period,
            actor=self.admin,
        )
        SettlementEngineService.finalize_settlement_period(
            period=period,
            actor=self.admin,
        )

        wallet = Wallet.objects.get(
            website=self.website,
            owner_user=self.writer_user,
            wallet_type=WalletType.WRITER,
        )
        self.assertEqual(wallet.available_balance, Decimal("240.00"))
        self.assertEqual(
            WalletEntry.objects.filter(
                wallet=wallet,
                reference_type=CompensationWalletSyncService.SETTLEMENT_REFERENCE_TYPE,
                reference_id=str(period.id),
            ).count(),
            1,
        )

    def test_mark_payout_paid_captures_writer_wallet_funds_once(self):
        period = SettlementPeriod.objects.create(
            website=self.website,
            writer=self.writer_profile,
            payment_window=self.window,
            status=SettlementStatus.COMPLETED,
            net_payable=Decimal("180.00"),
        )
        CompensationWalletSyncService.credit_settlement_to_wallet(
            period=period,
            actor=self.admin,
        )
        batch = PayoutBatch.objects.create(
            website=self.website,
            payment_window=self.window,
            title="May Batch",
            created_by=self.admin,
        )
        record = PayoutRecord.objects.create(
            website=self.website,
            batch=batch,
            writer=self.writer_profile,
            settlement_period=period,
            total_amount=Decimal("180.00"),
            status=PayoutRecordStatus.CONFIRMED,
        )

        PayoutEngineService.mark_record_paid(
            record=record,
            paid_by=self.admin,
            notes="Paid externally",
        )

        wallet = Wallet.objects.get(
            website=self.website,
            owner_user=self.writer_user,
            wallet_type=WalletType.WRITER,
        )
        hold = WalletHold.objects.get(
            wallet=wallet,
            reference_type=CompensationWalletSyncService.PAYOUT_REFERENCE_TYPE,
            reference_id=str(record.id),
        )
        self.assertEqual(hold.status, WalletHoldStatus.CAPTURED)
        self.assertEqual(wallet.available_balance, Decimal("0.00"))
        self.assertEqual(wallet.pending_balance, Decimal("0.00"))
