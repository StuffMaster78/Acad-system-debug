from __future__ import annotations

from governance.context import GovernanceContext
from governance.exceptions import RiskThresholdExceededError


class RiskInterceptor:
    """
    Blocks dangerous commands dynamically.
    """

    MAX_RISK_SCORE = 80.0

    def process(
        self,
        ctx: GovernanceContext,
    ) -> GovernanceContext:

        if ctx.risk_score >= self.MAX_RISK_SCORE:
            raise RiskThresholdExceededError(
                f"Risk score too high: {ctx.risk_score}"
            )

        return ctx