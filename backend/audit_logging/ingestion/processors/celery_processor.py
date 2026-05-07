from audit_logging.ingestion.processors.base_processor import BaseProcessor
from audit_logging.models.audit_event import AuditEvent
from audit_logging.tasks import process_audit_event_task


class CeleryProcessor(BaseProcessor):
    """
    Offloads heavy or external processing to Celery.
    """

    def process(self, event: AuditEvent) -> None:
        process_audit_event_task.delay(event.event_id)