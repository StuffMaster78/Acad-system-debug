from governance.contracts.decision import Decision
from governance.contracts.command import Command
from governance.policies.engine import PolicyEngine


class DecisionEngine:
    """
    Converts raw policy outputs into final governance decision.
    """

    @staticmethod
    def evaluate(command: Command) -> Decision:

        policy = PolicyEngine.evaluate(command)

        # HARD BLOCK
        if not policy.allowed:
            return Decision(
                allowed=False,
                requires_approval=policy.requires_approval,
                risk_score=policy.risk_score,
                blocked_reason=policy.reason,
                matched_policies=policy.matched_rules,
            )

        # RISK GATING
        requires_approval = (
            policy.requires_approval or policy.risk_score > 75
        )

        return Decision(
            allowed=not requires_approval,
            requires_approval=requires_approval,
            risk_score=policy.risk_score,
            matched_policies=policy.matched_rules,
        )