from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_payments_management.models.settlement_period_models import SettlementPeriod


class SettlementValidationService:
    """
    Validates settlement integrity before finalization.

    This is a safety gate before money moves.
    """

    @staticmethod
    def validate(
        *,
        period: SettlementPeriod,
    ) -> dict[str, Any]:

        issues: list[str] = []

        if period.net_payable < Decimal("0.00"):
            issues.append("NEGATIVE_NET_PAYABLE")

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
            raise ValueError(f"Settlement invalid: {result['issues']}")