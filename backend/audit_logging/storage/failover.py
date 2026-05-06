import logging
from datetime import datetime
from audit_logging.storage.dlq_store import DeadLetterQueueStore

logger = logging.getLogger("audit_logging")


class AuditFailover:
    """
    Handles audit failures without breaking business flows.

    This is your last-resort safety layer.
    """

    @staticmethod
    def capture(event, error: Exception):
        try:
            logger.error(
                "AUDIT_FAILURE",
                extra={
                    "event_id": getattr(event, "event_id", None),
                    "action": getattr(event, "action", None),
                    "error": str(error),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            DeadLetterQueueStore.push(event, str(error))

        except Exception:
            # absolute last resort
            pass