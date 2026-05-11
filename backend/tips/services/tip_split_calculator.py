from __future__ import annotations

from decimal import Decimal

from tips.models.tip_policy import TipPolicy


class TipSplitCalculator:
    """
    Pure deterministic financial calculator.

    No DB access.
    No side effects.
    """

    @staticmethod
    def calculate(
        *,
        policy: TipPolicy,
        gross_amount: Decimal,
    ) -> dict[str, Decimal]:

        writer_amount = (
            gross_amount
            * policy.writer_percentage
            / Decimal("100")
        )

        platform_amount = gross_amount - writer_amount

        return {
            "gross_amount": gross_amount,
            "writer_amount": writer_amount,
            "platform_amount": platform_amount,
        }