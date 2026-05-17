from audit_logging.services.audit_service import AuditService
from notifications_system.services.notification_service import NotificationService


class GovernanceInterceptors:
    """
    Side-effect orchestrator AFTER decisions are made.
    """

    @staticmethod
    def on_command_approved(command, actor, tenant):
        AuditService.record(
            action="command.approved",
            actor=actor,
            website=tenant,
            obj=command,
            metadata=command.to_dict(),
        )

        NotificationService.notify_role(
            event_key=command.event_key,
            role="admins",
            website=command.website,
            context=command.context,
        )

    @staticmethod
    def on_command_rejected(command, actor, tenant):
        AuditService.record(
            action="command.rejected",
            actor=actor,
            website=tenant,
            obj=command,
            metadata=command.to_dict(),
        )

        NotificationService.notify_role(
            event_key=command.event_key,
            role="superadmins",
            website=command.website,
            context=command.context,
        )