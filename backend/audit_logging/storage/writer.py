import logging

from django.core.exceptions import ValidationError

from audit_logging.models.audit_event import AuditEvent
from audit_logging.recovery.failure_capture import AuditFailureCapture
from audit_logging.tracing.trace import Trace

logger = logging.getLogger("audit")


class AuditWriter:
    """
    Canonical persistence boundary.

    Guarantees:
    - tenant isolation
    - deterministic writes
    - single source of truth for validation at persistence layer
    """

    def write(self, event: AuditEvent) -> AuditEvent | None:
        try:
            trace = Trace.snapshot()
            expected_website = trace.get("website_id")

            if not expected_website:
                raise ValidationError("Missing tenant context")

            if event.website is None:
                raise ValidationError("AuditEvent.website required")

            if str(event.website.id) != str(expected_website):
                raise ValidationError("Cross-tenant write blocked")

            if event.object_id is not None:
                event.object_id = str(event.object_id)

            if event.metadata is None:
                event.metadata = {}

            event.save()
            return event

        except Exception as exc:
            AuditFailureCapture.capture(event, exc)
            return None