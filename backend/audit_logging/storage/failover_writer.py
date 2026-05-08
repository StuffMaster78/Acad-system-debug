import logging

from audit_logging.recovery.failure_capture import AuditFailureCapture
from audit_logging.models.audit_event import AuditEvent

logger = logging.getLogger("audit_logging")


class AuditFailoverWriter:
    """
    Emergency fallback persistence path.

    Pure IO boundary.
    No validation. No rules. No logic.
    """

    def write(self, event: AuditEvent) -> AuditEvent | None:
        try:
            event.save()
            return event

        except Exception as exc:
            logger.warning(
                "AUDIT_FAILOVER_TRIGGERED",
                extra={
                    "event_id": getattr(event, "id", None),
                    "action": getattr(event, "action", None),
                },
            )

            AuditFailureCapture.capture(event, exc)
            return None