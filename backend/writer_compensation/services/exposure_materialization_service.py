from __future__ import annotations

from decimal import Decimal
from django.db import transaction

from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)

class ExposureMaterializationService:
    """
    Idempotent exposure materializer.

    RULE:
        ExposureLedger = deterministic projection of SettlementPeriod

    No incremental updates allowed.
    """

    @staticmethod
    def get_ledger(*, period: SettlementPeriod) -> ExposureLedger:
        ledger, _ = ExposureLedger.objects.get_or_create(
            website=period.website,
            writer=period.writer,
        )
        return ledger

    @staticmethod
    @transaction.atomic
    def materialize_from_settlement(
        *,
        period: SettlementPeriod,
    ) -> ExposureLedger:

        ledger = ExposureMaterializationService.get_ledger(period=period)

        # -----------------------------
        # RESET-BASED MATERIALIZATION
        # (prevents double counting)
        # -----------------------------
        ledger.total_earned = period.gross_earnings
        ledger.total_bonuses = period.total_bonuses
        ledger.total_deductions = period.total_deductions
        ledger.total_settled = period.net_payable
        ledger.total_advance_taken = period.total_advances

        ledger.recoverable_balance = (
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
        )

        ledger.save()

        return ledger
    
    @staticmethod
    def materialize_from_event(ce: CompensationEvent):
        """
        Bridge method for event-driven updates.

        Converts FinancialEvent → settlement-aware exposure update.

        WARNING:
            This should NOT bypass SettlementEngine logic in full rebuild mode.
            Only safe for incremental exposure tracking.
        """
        ledger, _ = ExposureLedger.objects.get_or_create(
            website=ce.website,
            writer=ce.writer,
        )

        # minimal safe increment mapping
        if ce.event_type in ["ORDER_EARNING", "SPECIAL_ORDER_EARNING", "CLASS_EARNING"]:
            ledger.total_earned += ce.amount

        elif ce.event_type == "BONUS":
            ledger.total_bonuses += ce.amount

        elif ce.event_type == "DEDUCTION":
            ledger.total_deductions += ce.amount

        ledger.recoverable_balance = (
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
        )

        ledger.save()