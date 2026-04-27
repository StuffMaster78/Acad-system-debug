from __future__ import annotations

import logging
from typing import Any, Optional

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from audit_logging.models import AuditLogEntry

logger = logging.getLogger("audit")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def async_log_audit(
    self,
    *,
    action: str,
    target: str = "",
    request_id: Optional[str] = None,
    target_id: Optional[int] = None,
    actor_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    changes: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    notes: str = "",
    timestamp: Any = None,
    target_content_type_id: Optional[int] = None,
    target_object_id: Optional[int] = None,
) -> int:
    """
    Persist an audit log entry asynchronously.

    Returns:
        int: Primary key of the created audit log entry.
    """
    actor = None
    UserModel = get_user_model()

    if actor_id is not None:
        try:
            actor = UserModel.objects.get(pk=actor_id)
        except UserModel.DoesNotExist:
            logger.warning(
                "[AUDIT] Actor with actor_id=%s does not exist.",
                actor_id,
            )

    try:
        if isinstance(timestamp, str):
            parsed_timestamp = parse_datetime(timestamp)
            if parsed_timestamp is not None:
                timestamp = parsed_timestamp

        if timestamp is None:
            timestamp = now()

        entry = AuditLogEntry.objects.create(
            action=action,
            actor=actor,
            target=target,
            target_id=target_id,
            request_id=request_id,
            metadata=metadata or {},
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent or "Unknown Agent",
            notes=notes or "",
            timestamp=timestamp,
            target_content_type_id=target_content_type_id,
            target_object_id=target_object_id,
        )

        logger.info(
            "[AUDIT] Async log complete: action=%s target=%s target_id=%s entry_id=%s",
            action,
            target,
            target_id,
            entry.pk,
        )

        return entry.pk

    except Exception as exc:
        logger.exception(
            (
                "[AUDIT] Async log failed: "
                "action=%s target=%s target_id=%s actor_id=%s error=%s"
            ),
            action,
            target,
            target_id,
            actor_id,
            str(exc),
        )
        raise