from __future__ import annotations

from typing import Callable
from django.http import HttpRequest, HttpResponse

from audit_logging.tracing.trace import Trace


class AuditContextMiddleware:
    """
    Injects audit context into Trace layer.

    Responsibilities:
    - correlation_id
    - website_id
    - actor_id (best effort)
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:

        self._bind_correlation(request)
        self._bind_website(request)
        self._bind_actor(request)

        return self.get_response(request)

    # -------------------------
    # Correlation ID
    # -------------------------

    def _bind_correlation(self, request: HttpRequest) -> None:
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.META.get("HTTP_X_CORRELATION_ID")
        )

        if not correlation_id:
            return

        Trace.set_correlation_id(correlation_id)

    # -------------------------
    # Website / tenant context
    # -------------------------

    def _bind_website(self, request: HttpRequest) -> None:
        website = getattr(request, "website", None)

        if not website:
            return

        website_id = getattr(website, "id", None)

        if website_id:
            Trace.set_website_id(str(website_id))

    # -------------------------
    # Actor context
    # -------------------------

    def _bind_actor(self, request: HttpRequest) -> None:
        user = getattr(request, "user", None)

        if not user or not getattr(user, "is_authenticated", False):
            return

        # attach for downstream systems (optional future Trace enhancement)
        setattr(request, "_audit_actor_id", getattr(user, "id", None))