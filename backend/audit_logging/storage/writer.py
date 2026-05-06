from audit_logging.storage.models import AuditEvent
from audit_logging.storage.failover import AuditFailover

class AuditWriter:
    """
    DB persistence layer.
    """

    def write(self, event: AuditEvent):
        try:
            event.save()
            return event
        except Exception as e:
            # Never block business logic
            AuditFailover.capture(event, e)
            return None