from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError

from audit_logging.ingestion.recorder import AuditRecorder
from audit_logging.models.audit_event import AuditEvent
from audit_logging.services.audit_validator import AuditValidator
from audit_logging.tracing.context import TraceContext

logger = logging.getLogger("audit")


class AuditService:
    """
    Canonical audit write service.

    This is the ONLY valid write entry-point for audit events.
    """

    @classmethod
    def record(
        cls,
        *,
        action: str,
        actor: Any | None = None,
        website: Any | None = None,
        obj: Any | None = None,
        metadata: dict[str, Any] | None = None,
        request: Any | None = None,
        severity: str = "info",
        is_sensitive: bool = False,
        sensitivity_level: str | None = None,
        service_name: str | None = None,
        idempotency_key: str | None = None,
    ) -> AuditEvent:

        metadata = metadata or {}

        # -------------------------
        # Validation
        # -------------------------
        AuditValidator.validate(action=action, metadata=metadata)

        # -------------------------
        # Trace context (safe read-only snapshot)
        # -------------------------
        correlation_id = TraceContext.get_correlation_id()
        current_span = TraceContext.current_span()
        website_ctx = TraceContext.get_website_id()

        # -------------------------
        # Tenant resolution (deterministic)
        # -------------------------
        resolved_website = website

        if resolved_website is None and request is not None:
            resolved_website = getattr(request, "website", None)

        if resolved_website is None and website_ctx is not None:
            resolved_website = website_ctx

        if resolved_website is None:
            raise ValidationError("Audit event requires website context")

        website_id_value = getattr(resolved_website, "id", resolved_website)

        # -------------------------
        # Actor
        # -------------------------
        actor_id = getattr(actor, "id", None)

        # -------------------------
        # Object
        # -------------------------
        object_type = obj.__class__.__name__ if obj else None
        object_id = str(getattr(obj, "id", None)) if obj else None

        # -------------------------
        # Request context (safe extraction)
        # -------------------------
        ip_address = None
        user_agent = None

        if request is not None:
            meta = getattr(request, "META", None) or {}
            ip_address = meta.get("REMOTE_ADDR")
            user_agent = meta.get("HTTP_USER_AGENT")

        # -------------------------
        # Trace enrichment (null-safe)
        # -------------------------
        span_id = getattr(current_span, "span_id", None)

        # -------------------------
        # Event construction
        # -------------------------
        event = AuditEvent(
            website=resolved_website,

            action=action,
            actor_id=actor_id,

            object_type=object_type,
            object_id=object_id,

            correlation_id=correlation_id,
            span_id=span_id,

            ip_address=ip_address,
            user_agent=user_agent,

            metadata=metadata,

            severity=severity,

            is_sensitive=is_sensitive,
            sensitivity_level=sensitivity_level,

            service_name=service_name,

            idempotency_key=idempotency_key,
        )

        # -------------------------
        # Single ingestion boundary
        # -------------------------
        persisted_event = AuditRecorder.ingest(event)

        logger.info(
            "Audit event recorded",
            extra={
                "action": action,
                "website_id": website_id_value,
                "object_type": object_type,
                "object_id": object_id,
            },
        )

        return persisted_event