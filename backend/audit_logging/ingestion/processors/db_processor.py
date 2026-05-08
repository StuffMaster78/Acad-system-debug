from audit_logging.ingestion.processors.base_processor import BaseProcessor
from audit_logging.models.audit_event import AuditEvent


class DBProcessor(BaseProcessor):
    """
    Secondary persistence / replication layer.

    Rule:
    - MUST NOT modify original AuditEvent
    - ONLY copy or forward
    """

    def process(self, event: AuditEvent) -> None:
        # safe no-op placeholder OR replication logic

        # Example: if you later add audit replica table:
        # AuditEventReplica.objects.create(...)

        pass