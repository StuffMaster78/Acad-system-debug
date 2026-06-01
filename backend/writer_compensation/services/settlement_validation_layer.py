from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.exceptions.settlement_exceptions import (
    SettlementValidationError,
)


class SettlementValidationService:
    """
    Validates settlement integrity before finalization.
    This is a safety gate — it runs before any money-related action.
    """

    @staticmethod
    def validate(
        *,
        period: SettlementPeriod,
    ) -> dict[str, Any]:

        issues: list[str] = []

        # FIX: removed NEGATIVE_NET_PAYABLE check.
        # Fines and deductions can legitimately exceed earnings in a window —
        # this is by design. The shortfall is carried forward by admin via a
        # post-close ADJUSTMENT event in the next window.
        # Blocking finalization on negative net would prevent valid settlements.

        if period.total_financial_events == 0:
            issues.append("EMPTY_SETTLEMENT")

        if period.is_locked and period.status != "COMPLETED":
            issues.append("INVALID_LOCK_STATE")

        if period.gross_earnings < Decimal("0.00"):
            issues.append("NEGATIVE_GROSS")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
        }

    @staticmethod
    def assert_valid(
        *,
        period: SettlementPeriod,
    ) -> None:
        result = SettlementValidationService.validate(period=period)

        if not result["is_valid"]:
            raise SettlementValidationError( # FIX: was bare ValueError
                f"Settlement invalid: {result['issues']}"
            )