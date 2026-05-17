from __future__ import annotations

from governance.context import GovernanceContext
from governance.exceptions import RollbackExecutionError


class RollbackExecutor:
    """
    Executes reversal operations safely.
    """

    @staticmethod
    def rollback(
        ctx: GovernanceContext,
    ) -> None:

        if ctx.command_type == "user.suspend":
            RollbackExecutor._unsuspend_user(ctx)
            return

        if ctx.command_type == "user.blacklist":
            RollbackExecutor._unblacklist_user(ctx)
            return

        raise RollbackExecutionError(
            f"No rollback handler for {ctx.command_type}"
        )

    @staticmethod
    def _unsuspend_user(
        ctx: GovernanceContext,
    ) -> None:

        from users.models import User

        User.objects.filter(
            id=ctx.payload["user_id"],
        ).update(
            is_suspended=False,
        )

    @staticmethod
    def _unblacklist_user(
        ctx: GovernanceContext,
    ) -> None:

        from users.models import User

        User.objects.filter(
            id=ctx.payload["user_id"],
        ).update(
            is_blacklisted=False,
        )