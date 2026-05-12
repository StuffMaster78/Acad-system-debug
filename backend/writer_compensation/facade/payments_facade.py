from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_compensation.factories.correction_event_factory import CorrectionEventFactory
from writer_compensation.services.settlement_engine_service import SettlementEngineService
from writer_compensation.services.settlement_validation_layer import SettlementValidationService
from writer_compensation.services.risk_engine_service import RiskEngineService
from writer_compensation.services.reconciliation_service import ReconciliationService
from writer_compensation.services.exposure_materialization_service import ExposureMaterializationService

class CompensationFacade:

    # -----------------------------
    # CORRECTIONS
    # -----------------------------
    @staticmethod
    def create_correction_event(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        source: str,
        created_by: Any | None = None,
        idempotency_key: str | None = None,
    ):
        CompensationFacade._validate_amount(amount)

        return CorrectionEventFactory.create(
            website=website,
            writer=writer,
            amount=amount,
            reason=reason,
            correction_type="SYSTEM_CORRECTION",
            source=source,
            created_by=created_by,
            idempotency_key=idempotency_key,
        )

    # -----------------------------
    # SETTLEMENT
    # -----------------------------
    @staticmethod
    def run_settlement(
        *,
        website: Any,
        writer: Any,
        payment_window: Any,
        auto_finalize: bool = True,
    ):
        period = SettlementEngineService.create_settlement_period(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )

        SettlementEngineService.build_settlement_snapshot(period=period)
        SettlementValidationService.assert_valid(period=period)
        SettlementEngineService.create_settlement_items(period=period)

        if auto_finalize:
            SettlementEngineService.finalize_settlement_period(period=period)

        return period

    # -----------------------------
    # RECONCILIATION (NEW BOUNDARY)
    # -----------------------------
    @staticmethod
    def run_reconciliation(
        *,
        website: Any,
        batch: Any,
        ledger_total: Decimal,
        payout_total: Decimal,
        cleared_total: Decimal,
    ):
        return ReconciliationService.create_report(
            website=website,
            batch=batch,
            ledger_total=ledger_total,
            payout_total=payout_total,
            cleared_total=cleared_total,
        )

    # -----------------------------
    # EXPOSURE MATERIALIZATION (NEW BOUNDARY)
    # -----------------------------
    @staticmethod
    def materialize_exposure(*, settlement_period: Any):
        return ExposureMaterializationService.materialize_from_settlement(
            period=settlement_period
        )

    # -----------------------------
    # WALLET (READ ONLY)
    # -----------------------------
    @staticmethod
    def get_wallet_balance(*, wallet: Any):
        return wallet.available_balance

    # -----------------------------
    # RISK
    # -----------------------------
    @staticmethod
    def can_issue_advance(*, ledger: Any, amount: Decimal) -> bool:
        return RiskEngineService.can_issue_advance(
            ledger=ledger,
            amount=amount,
        )

    # -----------------------------
    # GUARDS
    # -----------------------------
    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal")

        if amount <= Decimal("0.00"):
            raise ValueError("amount must be greater than zero")


PaymentsFacade = CompensationFacade
