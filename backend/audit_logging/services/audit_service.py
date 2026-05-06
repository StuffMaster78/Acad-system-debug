from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError

from audit_logging.storage.models import AuditEvent
from audit_logging.utils.ids import generate_event_id
from audit_logging.services.audit_validator import AuditValidator
from audit_logging.ingestion.recorder import AuditRecorder
from audit_logging.tracing.context import TraceContext

logger = logging.getLogger("audit")


class AuditService:
    """
    Core audit write service.

    Rules:
    1. Single entry point for AuditEvent creation.
    2. No async logic.
    3. No external integrations.
    4. Only normalization + trace enrichment + persistence.
    """

    @classmethod
    def record(
        cls,
        *,
        action: str,
        actor=None,
        website,
        obj: Any | None = None,
        metadata: dict[str, Any] | None = None,
        request: Any | None = None,
        span: Any | None = None,
        correlation_id: str | None = None,
        is_sensitive: bool = False,
        sensitivity_level: str | None = None,
        source: str = "system",
    ) -> AuditEvent:

        metadata = metadata or {}

        if not AuditValidator.validate(action, metadata):
            raise ValidationError(f"Invalid audit action: {action}")
        
        if website is None and request is not None:
            website = getattr(request, "website", None)

        if website is None:
            raise ValidationError(
                "AuditEvent requires website (multi-tenant enforcement)"
            )

        # ----------------------------
        # Trace context (single source of truth)
        # ----------------------------
        ctx = TraceContext.current() or type("EmptyCtx", (), {})()

        span = span or getattr(ctx, "span", None)
        correlation_id = correlation_id or getattr(ctx, "correlation_id", None)
        parent_span = TraceContext.current_span()

        parent_span_id = getattr(parent_span, "span_id", None)
        span_depth = TraceContext.depth()
        # ----------------------------
        # Actor resolution
        # ----------------------------
        actor_id = getattr(actor, "id", None) if actor else None
        actor_type = getattr(actor, "__class__", type(None)).__name__ if actor else None

        # ----------------------------
        # Object resolution
        # ----------------------------
        object_type = None
        object_id = None

        if obj is not None:
            object_type = obj.__class__.__name__
            object_id = getattr(obj, "id", None)

        # ----------------------------
        # Request context (safe)
        # ----------------------------
        request_id = getattr(request, "request_id", None) if request else None

        ip_address = (
            request.META.get("REMOTE_ADDR")
            if request and hasattr(request, "META")
            else None
        )

        user_agent = (
            request.META.get("HTTP_USER_AGENT")
            if request and hasattr(request, "META")
            else None
        )

        # ----------------------------
        # Span enrichment (ONLY ONCE)
        # ----------------------------
        span = span or getattr(ctx, "span", None)

        span_id = getattr(span, "span_id", None) if span else None
        span_name = getattr(span, "name", None) if span else None
        span_start_ms = getattr(span, "start_ms", None)
        span_duration_ms = span.duration_ms() if span else None

        # ----------------------------
        # Event construction
        # ----------------------------
        event = AuditEvent(
            event_id=generate_event_id(),
            action=action,

            actor_id=actor_id,
            actor_type=actor_type,

            object_type=object_type,
            object_id=str(object_id) if object_id else None,

            request_id=request_id,
            correlation_id=correlation_id,

            ip_address=ip_address,
            user_agent=user_agent,

            span_id=span_id,
            span_name=span_name,
            span_start_ms=span_start_ms,
            span_duration_ms=span_duration_ms,
            parent_span_id=parent_span_id,
            span_depth=span_depth,

            metadata=metadata,

            is_sensitive=is_sensitive,
            sensitivity_level=sensitivity_level,
            source=source,
        )

        event.save()

        return AuditRecorder.ingest(event)