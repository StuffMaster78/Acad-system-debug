from celery import shared_task
from audit_logging.services.audit_service import AuditService


@shared_task
def handle_audit_event(event_payload: dict):
    """
    Writes compliance-grade audit logs.
    """

    AuditService.record(
        action=f"user_state.{event_payload.get('type')}",
        actor=event_payload.get("actor"),
        obj=event_payload.get("user"),
        metadata=event_payload,
        severity="info",
        service_name="users_state",
    )