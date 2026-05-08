from audit_logging.ingestion.processors.base_processor import BaseProcessor
from audit_logging.models.audit_event import AuditEvent
from audit_logging import tasks


class CeleryProcessor(BaseProcessor):
    """
    Offloads processing to Celery asynchronously.
    """

    def process(self, event: AuditEvent) -> None:
        tasks.process_audit_event_task.delay(str(event.id)) # pyright: ignore[reportCallIssue]