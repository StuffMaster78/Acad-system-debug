from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction

from wallets.constants import WalletEntryType, WalletHoldStatus
from wallets.models import WalletEntry, WalletHold
from wallets.services import WalletHoldService, WalletService, WriterWalletService


class CompensationWalletSyncService:
    """
    Bridges writer_compensation financial state into canonical wallets.

    CompensationEvent/SettlementPeriod remain the earnings truth. The wallets
    app owns spendable balances, payout reserves, and payout settlement.
    """

    SETTLEMENT_REFERENCE_TYPE = "writer_compensation_settlement"
    PAYOUT_REFERENCE_TYPE = "writer_compensation_payout"

    @staticmethod
    @transaction.atomic
    def credit_settlement_to_wallet(
        *,
        period,
        actor: Any | None = None,
    ):
        amount = Decimal(str(period.net_payable))
        if amount <= Decimal("0.00"):
            return None

        existing_entry = WalletEntry.objects.filter(
            website=period.website,
            reference_type=CompensationWalletSyncService.SETTLEMENT_REFERENCE_TYPE,
            reference_id=str(cast(Any, period).id),
            entry_type=WalletEntryType.EARNING,
        ).first()
        if existing_entry is not None:
            return existing_entry

        wallet = WriterWalletService.get_wallet(
            website=period.website,
            writer=CompensationWalletSyncService._writer_user(period.writer),
        )
        return WalletService.credit_wallet(
            wallet=wallet,
            website=period.website,
            amount=amount,
            entry_type=WalletEntryType.EARNING,
            created_by=actor,
            description=(
                "Writer settlement credited "
                f"for {period.payment_window.title}"
            ),
            reference=f"SETTLEMENT-{cast(Any, period).id}",
            reference_type=CompensationWalletSyncService.SETTLEMENT_REFERENCE_TYPE,
            reference_id=str(cast(Any, period).id),
            metadata={
                "settlement_period_id": cast(Any, period).id,
                "payment_window_id": period.payment_window_id,
                "writer_profile_id": period.writer_id,
            },
        )

    @staticmethod
    @transaction.atomic
    def settle_payout_record(
        *,
        record,
        actor: Any | None = None,
    ):
        amount = Decimal(str(record.total_amount))
        if amount <= Decimal("0.00"):
            return None

        wallet = WriterWalletService.get_wallet(
            website=record.website,
            writer=CompensationWalletSyncService._writer_user(record.writer),
        )

        existing_hold = WalletHold.objects.filter(
            website=record.website,
            wallet=wallet,
            reference_type=CompensationWalletSyncService.PAYOUT_REFERENCE_TYPE,
            reference_id=str(cast(Any, record).id),
        ).first()

        if existing_hold is None:
            hold = WalletHoldService.create_hold(
                wallet=wallet,
                website=record.website,
                amount=amount,
                reason="Writer compensation payout",
                created_by=actor,
                reference=f"PAYOUT-{cast(Any, record).id}",
                reference_type=CompensationWalletSyncService.PAYOUT_REFERENCE_TYPE,
                reference_id=str(cast(Any, record).id),
                metadata={
                    "payout_record_id": cast(Any, record).id,
                    "payout_batch_id": record.batch_id,
                    "payment_window_id": record.batch.payment_window_id,
                    "writer_profile_id": record.writer_id,
                },
            )
        else:
            hold = existing_hold

        if hold.status == WalletHoldStatus.ACTIVE:
            return WalletHoldService.capture_hold(
                hold=hold,
                captured_by=actor,
            )

        return hold

    @staticmethod
    def _writer_user(writer_profile):
        return getattr(writer_profile, "user", None) or writer_profile.account_profile.user
