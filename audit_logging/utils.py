"""
Utilities for thread-safe request and user access using contextvars.
"""

import contextvars
from typing import Optional
from django.http import HttpRequest
from django.contrib.auth import get_user_model

_request_ctx: contextvars.ContextVar[Optional[HttpRequest]] = contextvars.ContextVar(
    "request", default=None
)


def set_current_request(request: HttpRequest) -> None:
    """
    Stores the current request in a context-local variable.

    Args:
        request (HttpRequest): The incoming request to store.
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
    request = _request_ctx.get()
    return getattr(request, "user", None) if request else None


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract User-Agent string from request."""
    return request.META.get('HTTP_USER_AGENT', '')
