from django.core.exceptions import ValidationError

from audit_logging.models.audit_event import AuditEvent
from audit_logging.recovery.failure_capture import AuditFailureCapture
from audit_logging.tracing.trace import Trace


class AuditWriter:
    """
    Low-level persistence gateway for AuditEvent.

    Responsibilities:
    - enforce invariants (tenant safety)
    - persist audit events
    - delegate failure handling
    - remain deterministic
    """

    def write(self, event: AuditEvent) -> AuditEvent | None:
        try:
            # -------------------------
            # Tenant enforcement (final guard)
            # -------------------------
            trace = Trace.snapshot()
            expected_website = trace.get("website_id")

            if not expected_website:
                raise ValidationError(
                    "Missing tenant context in Trace"
                )

            if event.website is None:
                raise ValidationError("AuditEvent.website is required")

            if str(event.website.id) != str(expected_website):
                raise ValidationError("Cross-tenant audit write blocked")

            # -------------------------
            # Defensive normalization
            # -------------------------
            if event.object_id is not None:
                event.object_id = str(event.object_id)

            if event.metadata is None:
                event.metadata = {}

            if event.actor_type is None and event.actor_id is not None:
                event.actor_type = "unknown"

            # -------------------------
            # Persist
            # -------------------------
            event.save()
            return event

        except Exception as exc:
            # Never block business flow
            AuditFailureCapture.capture(event, exc)
            return None