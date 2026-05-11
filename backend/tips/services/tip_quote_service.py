from __future__ import annotations

from decimal import Decimal

from tips.contracts.tip_quote_contract import TipQuoteContract
from tips.services.tip_policy_resolver import TipPolicyResolver
from tips.services.tip_split_calculator import TipSplitCalculator


class TipQuoteService:
    """
    Pre-payment breakdown generator.

    Pure UX service:
    - no DB writes
    - no side effects
    """

    @classmethod
    def quote(
        cls,
        *,
        gross_amount: Decimal,
    ) -> TipQuoteContract:

        policy = TipPolicyResolver.get_active_policy()

        breakdown = TipSplitCalculator.calculate(
            policy=policy,
            gross_amount=gross_amount,
        )

        return TipQuoteContract(
            gross_amount=breakdown["gross_amount"],
            writer_amount=breakdown["writer_amount"],
            platform_amount=breakdown["platform_amount"],
            currency="USD",
        )