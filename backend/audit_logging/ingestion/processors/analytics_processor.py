from audit_logging.ingestion.processors.base_processor import BaseProcessor
from audit_logging.storage.models import AuditEvent


class AnalyticsProcessor(BaseProcessor):

    def process(self, event: AuditEvent) -> None:
        if event.action.startswith("billing."):
            self._track_billing(event)

        if event.is_sensitive:
            self._track_sensitive(event)

    def _track_billing(self, event):
        pass  # later plug into Prometheus / internal metrics

    def _track_sensitive(self, event):
        pass  # compliance hooks