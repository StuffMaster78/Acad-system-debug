"""
Compatibility facade for legacy audit logging callers.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError

from audit_logging.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AuditLogService:
    """
    Legacy API backed by the canonical AuditService.
    """

    @classmethod
    def log(cls, **kwargs: Any):
        return cls.log_auto(**kwargs)

    @classmethod
    def log_auto(cls, **kwargs: Any):
        actor = kwargs.pop("actor", None) or kwargs.pop("user", None)
        action = kwargs.pop("action", "")
        target = kwargs.pop("target", None) or kwargs.pop("obj", None)
        metadata = kwargs.pop("metadata", None) or {}
        request = kwargs.pop("request", None)
        website = kwargs.pop("website", None) or getattr(target, "website", None)

        metadata.update(kwargs)

        try:
            return AuditService.record(
                action=action,
                actor=actor,
                website=website,
                obj=target,
                metadata=metadata,
                request=request,
            )
        except ValidationError:
            logger.debug("Skipped legacy audit event without website context.")
            return None
