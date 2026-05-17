from __future__ import annotations

from governance.context import GovernanceContext
from governance.decision_engine import DecisionEngine
from governance.exceptions import ApprovalRequiredError


class ApprovalInterceptor:
    """
    Routes commands into approval workflows.
    """

    def process(
        self,
        ctx: GovernanceContext,
    ) -> GovernanceContext:

        decision = DecisionEngine.evaluate(ctx)

        if decision.requires_approval:
            raise ApprovalRequiredError(
                f"Approval required for {ctx.command_type}"
            )

        return ctx