"""
writer_compensation/facade/payments_facade.py

Fixes applied:
  1. Both factory imports removed:
       - FinancialEventFactory (imported financial_event_models — deleted model)
       - CorrectionEventFactory (same crash)
     Both factories have been deleted. They were thin wrappers around
     CompensationEvent.objects.create() that bypassed EventIntakeService.
     EventIntakeService.record() is the correct creation path.

  2. create_correction_event() now delegates to AdjustmentService
     instead of CorrectionEventFactory. AdjustmentService routes
     through EventIntakeService correctly.

  3. _validate_amount() now allows negative amounts (was rejecting them
     with amount <= 0 check). Correction events and deductions are
     legitimately negative. Only zero is rejected.

  4. get_wallet_balance() now has a null guard — returns Decimal("0.00")
     if wallet is None rather than raising AttributeError.

  5. All imports are from unified compensation_enums only.

  6. materialize_exposure_from_event() added — allows the facade to
     trigger incremental ledger updates when a single event is created
     outside the settlement pipeline (e.g. real-time advance, fine).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_compensation.exceptions.exceptions import ZeroAmountError
from writer_compensation.services.adjustment_service import AdjustmentService
from writer_compensation.services.advance_payment_service import AdvancePaymentService
from writer_compensation.services.event_intake_service import EventIntakeService
from writer_compensation.services.exposure_materialization_service import (
    ExposureMaterializationService,
)
from writer_compensation.services.reconciliation_service import ReconciliationService
from writer_compensation.services.risk_engine_service import RiskEngineService
from writer_compensation.services.settlement_engine_service import SettlementEngineService
from writer_compensation.services.settlement_validation_layer import (
    SettlementValidationService,
)


class CompensationFacade:
    """
    Public surface for the writer compensation system.

    Callers outside this app (API views, other apps, management commands)
    should use this facade rather than importing services directly.
    This keeps inter-app coupling to one import boundary.

    Rules:
        - No business logic here — delegate everything to services.
        - No DB queries here — services and selectors own those.
        - All methods are static — no state on the facade.
    """

    # ------------------------------------------------------------------
    # Event creation
    # ------------------------------------------------------------------

    @staticmethod
    def record_event(
        *,
        website: Any,
        writer: Any,
        event_type: str,
        amount: Decimal,
        source_type: str = "",
        source_id: int | None = None,
        notes: str = "",
        idempotency_key: str = "",
        created_by: Any | None = None,
        related_window: Any | None = None,
    ) -> tuple:
        """
        Generic entry point for any CompensationEvent.
        Returns (event, created: bool).
        """
        CompensationFacade._validate_amount(amount)
        return EventIntakeService.record(
            website=website,
            writer=writer,
            event_type=event_type,
            amount=amount,
            source_type=source_type,
            source_id=source_id,
            notes=notes,
            idempotency_key=idempotency_key,
            created_by=created_by,
            related_window=related_window,
        )

    # ------------------------------------------------------------------
    # Corrections / adjustments
    # ------------------------------------------------------------------

    @staticmethod
    def create_correction_event(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        created_by: Any | None = None,
    ) -> Any:
        """
        FIX: was delegating to CorrectionEventFactory which imported a
        deleted model and crashed. Now delegates to AdjustmentService
        which routes through EventIntakeService correctly.

        Positive amount → credit correction (writer gets more)
        Negative amount → deduction correction (writer gets less)
        """
        CompensationFacade._validate_amount(amount)

        return AdjustmentService.apply_adjustment(
            website=website,
            writer=writer,
            amount=amount,
            reason=reason,
            created_by=created_by,
        )

    @staticmethod
    def create_post_close_adjustment(
        *,
        closed_window: Any,
        writer: Any,
        amount: Decimal,
        notes: str,
        created_by: Any,
    ) -> Any:
        """Post-close correction referencing a closed window."""
        CompensationFacade._validate_amount(amount)

        return AdjustmentService.create_post_close_adjustment(
            closed_window=closed_window,
            writer=writer,
            amount=amount,
            notes=notes,
            created_by=created_by,
        )

    # ------------------------------------------------------------------
    # Settlement
    # ------------------------------------------------------------------

    @staticmethod
    def run_settlement(
        *,
        website: Any,
        writer: Any,
        payment_window: Any,
        auto_finalize: bool = True,
    ) -> Any:
        """
        Full settlement pipeline for one writer in one window.
        Returns the SettlementPeriod.
        """
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

    # ------------------------------------------------------------------
    # Reconciliation
    # ------------------------------------------------------------------

    @staticmethod
    def run_reconciliation(
        *,
        website: Any,
        batch: Any,
        ledger_total: Decimal,
        payout_total: Decimal,
        cleared_total: Decimal,
    ) -> Any:
        return ReconciliationService.create_report(
            website=website,
            batch=batch,
            ledger_total=ledger_total,
            payout_total=payout_total,
            cleared_total=cleared_total,
        )

    # ------------------------------------------------------------------
    # Exposure materialization
    # ------------------------------------------------------------------

    @staticmethod
    def materialize_exposure(*, settlement_period: Any) -> Any:
        """Full ledger rebuild from a completed SettlementPeriod."""
        return ExposureMaterializationService.materialize_from_settlement(
            period=settlement_period,
        )

    @staticmethod
    def materialize_exposure_from_event(*, event: Any) -> Any:
        """
        Incremental ledger update from a single CompensationEvent.
        Use for real-time tracking between settlement runs.
        """
        return ExposureMaterializationService.materialize_from_event(event)

    @staticmethod
    def recompute_exposure(*, website: Any, writer: Any) -> Any:
        """
        Full ledger recompute directly from raw events.
        Use for reconciliation, drift detection, or disaster recovery.
        """
        return ExposureMaterializationService.recompute_from_events(
            website=website,
            writer=writer,
        )

    # ------------------------------------------------------------------
    # Advances
    # ------------------------------------------------------------------

    @staticmethod
    def can_issue_advance(*, ledger: Any, amount: Decimal) -> bool:
        """Pure eligibility check — does not modify any state."""
        return RiskEngineService.can_issue_advance(
            ledger=ledger,
            amount=amount,
        )

    @staticmethod
    def get_advance_cap(*, ledger: Any) -> Decimal:
        """Maximum advance amount this writer can request right now."""
        return RiskEngineService.get_advance_cap(ledger=ledger)

    @staticmethod
    def apply_advance(
        *,
        website: Any,
        writer: Any,
        ledger: Any,
        amount: Decimal,
        created_by: Any | None = None,
        advance_request: Any | None = None,
    ) -> Any:
        """
        Issue an advance. Updates ledger and fires ADVANCE CompensationEvent.
        Returns updated ExposureLedger.
        """
        return AdvancePaymentService.apply_advance(
            website=website,
            writer=writer,
            ledger=ledger,
            amount=amount,
            created_by=created_by,
            advance_request=advance_request,
        )

    @staticmethod
    def record_advance_recovery(
        *,
        website: Any,
        writer: Any,
        ledger: Any,
        advance_request: Any,
        amount: Decimal,
        settlement_period: Any | None = None,
        notes: str = "",
        created_by: Any | None = None,
    ) -> Any:
        """
        Record advance repayment. Creates AdvanceRecovery record and fires
        negative ADVANCE_RECOVERY CompensationEvent into current open window.
        """
        return AdvancePaymentService.record_recovery(
            website=website,
            writer=writer,
            ledger=ledger,
            advance_request=advance_request,
            amount=amount,
            settlement_period=settlement_period,
            notes=notes,
            created_by=created_by,
        )

    # ------------------------------------------------------------------
    # Wallet (read-only boundary)
    # ------------------------------------------------------------------

    @staticmethod
    def get_wallet_balance(*, wallet: Any) -> Decimal:
        """
        FIX: now has null guard. Returns Decimal("0.00") if wallet is None
        rather than raising AttributeError.
        """
        if wallet is None:
            return Decimal("0.00")
        return getattr(wallet, "available_balance", Decimal("0.00"))

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """
        FIX: was rejecting negative amounts (amount <= 0).
        Corrections, fines, and recoveries are legitimately negative.
        Only zero is invalid.
        """
        if not isinstance(amount, Decimal):
            raise TypeError(f"amount must be Decimal, got {type(amount).__name__}")

        if amount == Decimal("0.00"):
            raise ZeroAmountError("Amount cannot be zero.")


# Backward-compat alias — existing code using PaymentsFacade keeps working.
PaymentsFacade = CompensationFacade