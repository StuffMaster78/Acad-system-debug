import uuid
from audit_logging.tracing.context import TraceContext


class TraceMiddleware:
    """
    Request-level trace bootstrap.

    Responsibilities:
    - correlation_id
    - root span
    - website/tenant injection
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # -------------------------
        # Correlation ID
        # -------------------------
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            if hasattr(request, "headers")
            else None
        ) or str(uuid.uuid4())

        corr_token = TraceContext.set_correlation_id(correlation_id)
        request.correlation_id = correlation_id

        # -------------------------
        # Website / tenant
        # -------------------------
        website_id = getattr(request, "website", None) or getattr(request, "tenant", None)
        website_token = TraceContext.set_website_id(
            str(website_id) if website_id else None
        )

        # -------------------------
        # Root span
        # -------------------------
        root_span = TraceContext.create_root_span(
            f"{request.method} {request.path}"
        )

        TraceContext.push_span(root_span)
        request.span = root_span

        try:
            response = self.get_response(request)
            response["X-Correlation-ID"] = correlation_id
            return response

        finally:
            TraceContext.pop_span()
            TraceContext.reset_correlation_id(corr_token)
            TraceContext.reset_website_id(website_token)