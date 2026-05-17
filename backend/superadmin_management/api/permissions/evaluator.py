from superadmin_management.api.permissions.context import PermissionContext
from governance.policies.engine import PolicyEngine


class PermissionEvaluator:
    """
    Bridges PermissionEngine → PolicyEngine.
    """

    @staticmethod
    def evaluate(ctx: PermissionContext):
        return PolicyEngine.evaluate(
            command=ctx,
            actor=ctx.user_id,
            tenant=ctx.tenant_id,
        )