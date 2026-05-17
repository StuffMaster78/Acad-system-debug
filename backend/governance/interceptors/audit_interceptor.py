from governance.context import GovernanceContext
from audit_logging.services.audit_service import AuditService


class AuditInterceptor:

    def process(self, ctx: GovernanceContext) -> GovernanceContext:

        AuditService.record(
            action="governance.command.received",
            actor=ctx.user_id,
            metadata={
                "command_type": ctx.command_type,
                "payload": ctx.payload,
                "tenant_id": ctx.tenant_id,
            },
        )

        return ctx