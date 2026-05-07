import logging

from audit_logging.recovery.failure_capture import AuditFailureCapture
from audit_logging.models.audit_event import AuditEvent

logger = logging.getLogger("audit_logging")


class AuditFailoverWriter:
    """
    Emergency fallback persistence path for AuditEvent.

    This is NOT a primary writer.
    This is NOT a retry system.

    It exists only to:
    - attempt best-effort persistence
    - ensure failures are captured in DLQ
    - prevent audit system from crashing business flows
    """

    def write(self, event: AuditEvent) -> AuditEvent | None:
        try:
            # best-effort persistence
            event.save()
            return event

        except Exception as exc:
            logger.warning(
                "AUDIT_FAILOVER_TRIGGERED",
                extra={
                    "event_id": getattr(event, "event_id", None),
                    "action": getattr(event, "action", None),
                },
            )

            AuditFailureCapture.capture(event, exc)

            return None