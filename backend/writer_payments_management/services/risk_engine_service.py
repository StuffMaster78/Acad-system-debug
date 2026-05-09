from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_payments_management.models.exposure_ledger_models import ExposureLedger


class RiskEngineService:
    """
    Computes writer financial risk capacity.

    This is the enforcement layer for:
        - advance limits
        - exposure ceilings
        - risk-based financial safety

    RULE:
        This service NEVER mutates state.
        It only computes constraints.
    """

    ZERO = Decimal("0.00")
    HUNDRED = Decimal("100.00")

    @staticmethod
    def _safe_decimal(value: Any) -> Decimal:
        """
        Defensive conversion to Decimal.

        Prevents null / float / bad DB states from breaking calculations.
        """
        if value is None:
            return RiskEngineService.ZERO
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @staticmethod
    def get_available_risk_capacity(
        *,
        ledger: ExposureLedger,
    ) -> Decimal:
        """
        Maximum safe exposure allowed by platform policy.

        Formula:
            (total_earned × risk_cap_percentage) - total_advance_taken
        """

        total_earned = RiskEngineService._safe_decimal(ledger.total_earned)
        risk_cap_percentage = RiskEngineService._safe_decimal(
            ledger.risk_cap_percentage
        )
        used_advance = RiskEngineService._safe_decimal(
            ledger.total_advance_taken
        )

        max_allowed = (total_earned * risk_cap_percentage) / RiskEngineService.HUNDRED

        available = max_allowed - used_advance

        # Never allow negative risk capacity
        return available if available > RiskEngineService.ZERO else RiskEngineService.ZERO

    @staticmethod
    def can_issue_advance(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> bool:
        """
        Check whether an advance request is within safe risk boundaries.
        """

        if amount <= RiskEngineService.ZERO:
            return False

        available = RiskEngineService.get_available_risk_capacity(
            ledger=ledger,
        )

        return amount <= available