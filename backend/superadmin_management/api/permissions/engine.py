from __future__ import annotations

from superadmin_management.api.permissions.context import PermissionContext
from superadmin_management.api.permissions.roles import Role
from governance.policies.engine import PolicyEngine


class PermissionEngine:
    """
    Final authority for ALL authorization decisions.
    No other app is allowed to bypass this.
    """

    @staticmethod
    def can_execute_command(ctx: PermissionContext) -> bool:

        # 1. Superadmin override (still policy-aware but privileged)
        if ctx.role == Role.SUPERADMIN:
            return True

        # 2. Run policy engine
        decision = PolicyEngine.evaluate(
            command=ctx,
            actor=ctx.user_id,
            tenant=ctx.tenant_id,
        )

        # 3. Hard block if denied
        if not decision.allowed:
            return False

        # 4. Risk-based gating
        if decision.risk_score > 80:
            return False

        # 5. Approval-required check
        if decision.requires_approval:
            return False

        return True

    @staticmethod
    def requires_approval(ctx: PermissionContext) -> bool:

        decision = PolicyEngine.evaluate(
            command=ctx,
            actor=ctx.user_id,
            tenant=ctx.tenant_id,
        )

        return decision.requires_approval