import logging
from typing import Optional

from django.conf import settings
from django.utils.timezone import now

from audit_logging.models import AuditLogEntry
from audit_logging.tasks import async_log_audit
from audit_logging.middleware import get_current_request

logger = logging.getLogger("audit")


def _get_client_ip(request) -> Optional[str]:
    """
    Extract the client's IP address from the request object.
    """
    if not request:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]

    return request.META.get("REMOTE_ADDR")


def _get_user_agent(request) -> Optional[str]:
    """
    Return the User-Agent string from the request headers.
    """
    if not request:
        return None
    return request.META.get("HTTP_USER_AGENT", "")


def _sync_log_action(
    action: str,
    target: str = "",
    target_id: Optional[int] = None,
    actor=None,
    metadata: Optional[dict] = None
) -> AuditLogEntry:
    """
    Create a synchronous audit log entry.

    Args:
        action (str): Action performed (CREATE, UPDATE, etc).
        target (str): Target model in 'app.Model' format.
        target_id (int, optional): Primary key of the object.
        actor (User, optional): User who performed the action.
        metadata (dict, optional): Extra context or metadata.

    Returns:
        AuditLogEntry: The created log entry.
    """
    request = get_current_request()

    if not actor and request and hasattr(request, "user"):
        user = request.user
        actor = user if user.is_authenticated else None

    log = AuditLogEntry.objects.create(
        action=action,
        actor=actor,
        target=target,
        target_id=target_id,
        metadata=metadata or {},
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        timestamp=now()
    )

    logger.info(
        "[AUDIT] %s performed %s on %s(%s)",
        actor or "System", action, target, target_id
    )

    return log


def log_audit_action(
    action: str,
    target: str = "",
    target_id: Optional[int] = None,
    actor=None,
    metadata: Optional[dict] = None
):
    """
    Unified entry point for logging audit actions. Uses async if enabled.

    Args:
        action (str): Action performed (CREATE, UPDATE, etc).
        target (str): Target model in 'app.Model' format.
        target_id (int, optional): Primary key of the object.
        actor (User, optional): User performing the action.
        metadata (dict, optional): Additional context.

    Returns:
        AuditLogEntry | AsyncResult | None: Depends on strategy used.
    """
    request = get_current_request()
    use_async = getattr(settings, "USE_ASYNC_AUDIT_LOGGING", False)

    if use_async:
        try:
            user_id = None
            if actor:
                user_id = actor.id
            elif request and hasattr(request, "user"):
                user = request.user
                if user.is_authenticated:
                    user_id = user.id

            return async_log_audit.delay(
                action=action,
                target=target,
                target_id=target_id,
                actor_id=user_id,
                metadata=metadata,
                ip_address=_get_client_ip(request),
                user_agent=_get_user_agent(request),
            )
        except Exception as e:
            logger.warning(
                "[AUDIT] Async logging failed, falling back to sync: %s", str(e)
            )

    return _sync_log_action(
        action=action,
        target=target,
        target_id=target_id,
        actor=actor,
        metadata=metadata
    )