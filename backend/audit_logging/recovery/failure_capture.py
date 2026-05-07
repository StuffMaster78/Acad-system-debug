import logging

from audit_logging.recovery.dlq_store import DeadLetterQueueStore

logger = logging.getLogger("audit_logging")


class AuditFailureCapture:
    """
    Handles audit system failures safely
    without impacting business flows.

    This is the emergency boundary:
    - logs the failure
    - persists event into DLQ
    - NEVER raises exceptions upward
    """

    @staticmethod
    def capture(event, error: Exception) -> None:
        event_id = getattr(event, "event_id", None)
        action = getattr(event, "action", None)

        try:
            logger.error(
                "AUDIT_FAILURE_CAPTURED",
                extra={
                    "event_id": event_id,
                    "action": action,
                    "error": str(error),
                },
            )

            DeadLetterQueueStore.push(
                event_data={
                    "event_id": str(event_id) if event_id else None,
                    "action": action,
                    "payload": getattr(event, "metadata", None),
                },
                error=str(error),
            )

        except Exception as fatal_error:
            # absolute last line of defense
            logger.critical(
                "AUDIT_FATAL_FAILURE",
                extra={
                    "original_event_id": event_id,
                    "capture_error": str(fatal_error),
                },
            )