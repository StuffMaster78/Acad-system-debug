import logging
from audit_logging.recovery.dlq_store import DeadLetterQueueStore

logger = logging.getLogger("audit_logging")


class AuditFailureCapture:
    """
    Emergency boundary only.
    Never writes directly to persistence layer.
    """

    @staticmethod
    def capture(event, error: Exception) -> None:
        event_id = getattr(event, "id", None)

        try:
            logger.error(
                "AUDIT_FAILURE_CAPTURED",
                extra={
                    "event_id": event.id,
                    "action": getattr(event, "action", None),
                    "error": str(error),
                },
            )

            DeadLetterQueueStore.push(
                event_data={
                    "event_id": str(event.id),
                    "action": getattr(event, "action", None),
                    "metadata": getattr(event, "metadata", None),

                    # IMPORTANT ADDITIONS
                    "website": getattr(event, "website_id", None),
                    "object_type": getattr(event, "object_type", None),
                    "object_id": getattr(event, "object_id", None),
                    "correlation_id": getattr(event, "correlation_id", None),
                    "span_id": getattr(event, "span_id", None),
                },
                error=str(error),
            )

        except Exception as fatal_error:
            logger.critical(
                "AUDIT_FATAL_FAILURE",
                extra={
                    "original_event_id": event.id,
                    "capture_error": str(fatal_error),
                },
            )