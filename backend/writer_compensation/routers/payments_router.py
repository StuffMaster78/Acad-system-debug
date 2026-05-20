from __future__ import annotations

from decimal import Decimal
from typing import Any

from wallets.services.wallet_service import WalletService
from wallets.constants import WalletEntryType
from writer_compensation.services.settlement_engine_service import SettlementEngineService
from writer_compensation.services.correction_event_service import CorrectionEventService


class CompensationRouter:
    """
    Central orchestration layer for compensation flows.

    This is NOT business logic.
    This is execution routing only.
    """

    # -------------------------
    # ENTRY: wallet operations
    # -------------------------
    @staticmethod
    def process_wallet_debit(
        *,
        wallet: Any,
        amount: Decimal,
        website: Any,
        actor: Any | None = None,
        reason: str = "",
    ):
        return WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            website=website,
            created_by=actor,
            entry_type=WalletEntryType.ADMIN_DEBIT,
            description=reason,
        )

    @staticmethod
    def process_wallet_credit(
        *,
        wallet: Any,
        amount: Decimal,
        website: Any,
        actor: Any | None = None,
        reason: str = "",
    ):
        return WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            website=website,
            created_by=actor,
            entry_type=WalletEntryType.ADMIN_CREDIT,
            description=reason,
        )

    # -------------------------
    # ENTRY: settlement flow
    # -------------------------
    @staticmethod
    def run_settlement_cycle(
        *,
        period: Any,
        actor: Any | None = None,
        auto_finalize: bool = True,
    ):
        """
        Full settlement pipeline.

        Order:
            1. build snapshot
            2. create items
            3. optionally finalize
        """

        SettlementEngineService.build_settlement_snapshot(period=period)
        SettlementEngineService.create_settlement_items(period=period)

        if auto_finalize:
            SettlementEngineService.finalize_settlement_period(
                period=period,
                actor=actor,
            )

        return period

    # -------------------------
    # ENTRY: correction flow
    # -------------------------
    @staticmethod
    def emit_correction(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        actor: Any | None = None,
    ):
        return CorrectionEventService.create_correction(
            website=website,
            writer=writer,
            amount=amount,
            reason=reason,
            created_by=actor,
        )


PaymentsRouter = CompensationRouter
