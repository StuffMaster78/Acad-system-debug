from governance.context import GovernanceContext
from governance.decision_engine import DecisionEngine


class PolicyInterceptor:

    def process(self, ctx: GovernanceContext) -> GovernanceContext:

        decision = DecisionEngine.evaluate(ctx)

        ctx.risk_score = decision.risk_score

        if not decision.allowed:
            raise PermissionError("Policy denied")

        return ctx