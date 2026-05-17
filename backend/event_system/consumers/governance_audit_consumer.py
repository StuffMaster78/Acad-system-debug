from audit_logging.services.audit_service import AuditService


class GovernanceAuditConsumer:

    @staticmethod
    def handle(event) -> None:

        AuditService.record(
            action=event.event_type,
            actor=None,
            website=event.tenant_id,
            obj=None,
            metadata=event.payload,
            severity="info",
        )