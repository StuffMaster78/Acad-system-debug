from __future__ import annotations

from governance.contracts.policy_result import PolicyResult
from governance.contracts.command import Command


class PolicyEngine:
    """
    Evaluates policies for a command.

    THIS MUST NEVER:
    - execute side effects
    - call services
    - trigger events

    Pure function mindset.
    """

    @staticmethod
    def evaluate(command: Command) -> PolicyResult:

        # TEMP RULES (we will later replace with DB graph)
        if command.command_type == "user.delete":
            return PolicyResult(
                allowed=False,
                requires_approval=True,
                risk_score=95.0,
                matched_rules=["hard_delete_block"],
                reason="Hard deletes require approval",
            )

        if command.command_type == "user.suspend":
            return PolicyResult(
                allowed=True,
                requires_approval=True,
                risk_score=60.0,
                matched_rules=["suspension_policy"],
            )

        return PolicyResult(
            allowed=True,
            requires_approval=False,
            risk_score=10.0,
            matched_rules=["default_allow"],
        )