"""
Utilities for thread-safe request and user access using contextvars.
"""

import contextvars
from typing import Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from audit_logging.models import AuditLogEntry

# Context variable to store request per thread
_request_ctx: contextvars.ContextVar[Optional[HttpRequest]] = contextvars.ContextVar(
    "request", default=None
)


def set_current_request(request: HttpRequest) -> None:
    """
    Stores the current request in a context-local variable.
    Call this from middleware.
    """
    _request_ctx.set(request)


def get_current_request() -> Optional[HttpRequest]:
    """
    Retrieves the request from the current context.

    Returns:
        Optional[HttpRequest]: The request, or None if not set.
    """
    return _request_ctx.get()


def get_current_user():
    """
    Returns the user from the current request context, if available.

    Returns:
        User or None: The currently authenticated user, or None.
    """
    request = get_current_request()
    if request and hasattr(request, "user"):
        return request.user if request.user.is_authenticated else None
    return None


def get_client_ip(request: Optional[HttpRequest]) -> Optional[str]:
    """
    Extract client IP from the request, if available.

    Args:
        request (HttpRequest): The request object.

    Returns:
        str or None: IP address or None.
    """
    if not request:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: Optional[HttpRequest]) -> Optional[str]:
    """
    Extract the User-Agent string from the request.

    Args:
        request (HttpRequest): The request object.

    Returns:
        str or None: User-Agent or None.
    """
    if not request:
        return None

    return request.META.get("HTTP_USER_AGENT", "")


def log_audit(
    action: str,
    actor=None,
    target: Optional[str] = None,
    target_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    changes: Optional[dict] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    notes: Optional[str] = None
) -> AuditLogEntry:
    """
    Synchronously logs an audit entry for critical actions and state changes.

    Args:
        action (str): One of CREATE, UPDATE, DELETE, etc.
        actor (User, optional): The user who performed the action.
        target (str, optional): Model path like 'orders.Order'.
        target_id (int, optional): Object ID.
        metadata (dict, optional): Extra context.
        changes (dict, optional): What changed.
        ip (str, optional): IP address.
        user_agent (str, optional): User-Agent string.
        notes (str, optional): Extra notes.

    Returns:
        AuditLogEntry: The created audit log entry.
    """
    return AuditLogEntry.objects.create(
        action=action,
        actor=actor,
        target=target,
        target_id=target_id,
        metadata=metadata or {},
        changes=changes,
        ip_address=ip,
        user_agent=user_agent,
        notes=notes,
    )