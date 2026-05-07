from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError

from audit_logging.utils.ids import generate_event_id
from audit_logging.services.audit_validator import AuditValidator
from audit_logging.storage.writer import AuditWriter
from audit_logging.tracing.trace import Trace
from audit_logging.models.audit_event import AuditEvent

logger = logging.getLogger("audit")


class AuditService:
    """
    Core audit write service.

    Responsibilities:
    - validate audit intent
    - enforce tenant context (STRICT)
    - enrich with trace context
    - construct event
    - delegate persistence
    """

    writer = AuditWriter()

    @classmethod
    def record(
        cls,
        *,
        action: str,
        actor=None,
        website=None,
        obj: Any | None = None,
        metadata: dict[str, Any] | None = None,
        request: Any | None = None,
        is_sensitive: bool = False,
        sensitivity_level: str | None = None,
        source: str = "system",
    ):
        metadata = metadata or {}

        # ----------------------------
        # Validation
        # ----------------------------
        AuditValidator.validate(action, metadata)

        trace = Trace.snapshot()

        # ----------------------------
        # Tenant resolution (STRICT & SAFE)
        # ----------------------------
        if website is None:
            website = getattr(request, "website", None) if request else None

        if website is None:
            website_id = trace.get("website_id")

            if not website_id:
                raise ValidationError("Missing website (tenant context)")

            # last-resort safety: request must exist in valid flow
            if request is None:
                raise ValidationError("Cannot resolve website without request")

            website = getattr(request, "website", None)

        if website is None:
            raise ValidationError("Tenant resolution failed (website is None)")

        # ----------------------------
        # Trace context (single source of truth)
        # ----------------------------
        span = trace.get("span")
        correlation_id = trace.get("correlation_id")
        parent_span_id = trace.get("parent_span_id")

        # ----------------------------
        # Actor
        # ----------------------------
        actor_id = getattr(actor, "id", None) if actor else None
        actor_type = actor.__class__.__name__ if actor else None

        # ----------------------------
        # Object
        # ----------------------------
        object_type = obj.__class__.__name__ if obj else None
        object_id = str(getattr(obj, "id", None)) if obj else None

        # ----------------------------
        # Request context
        # ----------------------------
        request_id = getattr(request, "request_id", None) if request else None

        ip_address = (
            getattr(request, "META", {}).get("REMOTE_ADDR")
            if request
            else None
        )

        user_agent = (
            getattr(request, "META", {}).get("HTTP_USER_AGENT")
            if request
            else None
        )

        # ----------------------------
        # Span enrichment (safe)
        # ----------------------------
        span_id = getattr(span, "span_id", None) if span else None
        span_name = getattr(span, "name", None) if span else None
        span_duration_ms = span.duration_ms() if span else None

        # ----------------------------
        # Event construction
        # ----------------------------
        event = AuditEvent(
            event_id=generate_event_id(),
            action=action,

            website=website,

            actor_id=actor_id,
            actor_type=actor_type,

            object_type=object_type,
            object_id=object_id,

            request_id=request_id,
            correlation_id=correlation_id,

            ip_address=ip_address,
            user_agent=user_agent,

            span_id=span_id,
            span_name=span_name,
            parent_span_id=parent_span_id,
            span_duration_ms=span_duration_ms,

            metadata=metadata,

            is_sensitive=is_sensitive,
            sensitivity_level=sensitivity_level,
            source=source,
        )

        # ----------------------------
        # Persistence ONLY
        # ----------------------------
        return cls.writer.write(event)