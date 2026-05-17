from governance.context import GovernanceContext
from superadmin_management.api.permissions.engine import PermissionEngine


class PermissionInterceptor:

    def process(self, ctx: GovernanceContext) -> GovernanceContext:

        allowed = PermissionEngine.can_execute_command(
            ctx,
        )

        if not allowed:
            raise PermissionError("Permission denied")

        return ctx