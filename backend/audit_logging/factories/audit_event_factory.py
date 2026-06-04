from typing import Any

from django.db import transaction

from audit_logging.models.audit_event import AuditEvent, AuditSeverity
from audit_logging.tracing.trace import Trace
from audit_logging.utils.serialization import safe_serialize
from audit_logging.utils.validation import assert_valid_event_action
from audit_logging.services.stream.audit_stream import AuditStream

class AuditEventFactory:
    """
    Single authoritative audit event creation point.

    RULES:
    - no HTTP awareness
    - no async side effects
    - trace-driven context only
    - deterministic output
    """

    # -------------------------
    # CREATE EVENT
    # -------------------------

    @staticmethod
    @transaction.atomic
    def create(
        *,
        actor_id: int | None = None,
        actor_role: str | None = None,
        actor_display: str | None = None,
        action: str,
        website=None,
        object_type: str | None = None,
        object_id: str | None = None,
        metadata: dict | None = None,
        before: dict | None = None,
        after: dict | None = None,
        severity: str = AuditSeverity.INFO,
        is_sensitive: bool = False,
        sensitivity_level: str | None = None,
        service_name: str | None = None,
        idempotency_key: str | None = None,
    ) -> AuditEvent:

        assert_valid_event_action(action)

        # -------------------------
        # TRACE IS SOURCE OF TRUTH
        # -------------------------
        correlation_id = Trace.get_correlation_id()
        span = Trace.current_span()
        website_id = Trace.get_website_id()

        if website is None and website_id is None:
            raise RuntimeError("AuditEventFactory requires website context")

        # prefer explicit website over trace fallback
        final_website = website or website_id

        # -------------------------
        # Build enriched metadata
        # -------------------------
        enriched: dict[str, Any] = dict(metadata or {})
        if actor_role:
            enriched["actor_role"] = actor_role
        if actor_display:
            enriched["actor_display"] = actor_display
        if before is not None:
            enriched["before"] = before
        if after is not None:
            enriched["after"] = after

        # -------------------------
        # CREATE EVENT
        # -------------------------
        event = AuditEvent.objects.create(
            website=final_website,
            actor_id=actor_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            metadata=safe_serialize(enriched),
            correlation_id=correlation_id,
            span_id=getattr(span, "span_id", None),
            severity=severity,
            is_sensitive=is_sensitive,
            sensitivity_level=sensitivity_level,
            service_name=service_name,
            idempotency_key=idempotency_key,
        )

        AuditStream.publish(event)

        return event