from audit_logging.ingestion.processors.base_processor import BaseProcessor
from audit_logging.models.audit_event import AuditEvent


class DBProcessor(BaseProcessor):
    """
    Optional secondary persistence layer.
    Useful for:
    - audit replicas
    - reporting DB
    - long-term storage separation
    """

    def process(self, event: AuditEvent) -> None:
        # intentionally minimal
        event.save()