from __future__ import annotations

from decimal import Decimal
from django.db import transaction

from writer_payments_management.models.settlement_period_models import SettlementPeriod
from writer_payments_management.models.exposure_ledger_models import ExposureLedger
from writer_payments_management.models.financial_event_models import (
    FinancialEvent,
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
    def materialize_from_event(fe: FinancialEvent):
        """
        Bridge method for event-driven updates.

        Converts FinancialEvent → settlement-aware exposure update.

        WARNING:
            This should NOT bypass SettlementEngine logic in full rebuild mode.
            Only safe for incremental exposure tracking.
        """
        ledger, _ = ExposureLedger.objects.get_or_create(
            website=fe.website,
            writer=fe.writer,
        )

        # minimal safe increment mapping
        if fe.event_type in ["ORDER_EARNING", "SPECIAL_ORDER_EARNING", "CLASS_EARNING"]:
            ledger.total_earned += fe.amount

        elif fe.event_type == "BONUS":
            ledger.total_bonuses += fe.amount

        elif fe.event_type == "DEDUCTION":
            ledger.total_deductions += fe.amount

        ledger.recoverable_balance = (
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
        )

        ledger.save()