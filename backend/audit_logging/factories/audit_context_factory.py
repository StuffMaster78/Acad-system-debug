from typing import Any

from audit_logging.tracing.trace import Trace


class AuditContextFactory:

    @staticmethod
    def build(request: Any | None = None) -> dict:

        context = {
            "correlation_id": Trace.get_correlation_id(),
            "website_id": Trace.get_website_id(),
            "span_id": None,
            "ip_address": None,
            "user_agent": None,
            "actor_id": None,
        }

        span = Trace.current_span()

        if span:
            context["span_id"] = span.span_id

        if not request:
            return context

        user = getattr(request, "user", None)

        if user and getattr(user, "is_authenticated", False):
            context["actor_id"] = user.id

        context["ip_address"] = request.META.get(
            "REMOTE_ADDR"
        )

        context["user_agent"] = request.META.get(
            "HTTP_USER_AGENT"
        )

        website = getattr(request, "website", None)

        if website:
            context["website_id"] = website.id

        return context