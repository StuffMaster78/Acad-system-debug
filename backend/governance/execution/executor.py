from governance.context import GovernanceContext


class CommandExecutor:

    @staticmethod
    def execute(ctx: GovernanceContext):

        command = ctx.command

        # route to domain layer
        if command.command_type == "user.suspend":

            from superadmin_management.event_handlers.suspension_handlers import (
                handle_user_suspended,
            )

            return handle_user_suspended(command.payload)

        if command.command_type == "user.blacklist":

            from superadmin_management.event_handlers.blacklist_handlers import (
                handle_user_blacklisted,
            )

            return handle_user_blacklisted(command.payload)

        raise ValueError(f"Unknown command: {command.command_type}")