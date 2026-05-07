import uuid
from audit_logging.tracing.trace import (
    Trace,
)


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

        corr_token = Trace.set_correlation_id(correlation_id)
        request.correlation_id = correlation_id

        # -------------------------
        # Website / tenant
        # -------------------------
        website = getattr(request, "website", None)
        if not website:
            raise RuntimeError("Missing tenant (website) on request")

        website_id = str(getattr(website, "id", website))
                
        website_token = Trace.set_website_id(website_id)

        # -------------------------
        # Root span
        # -------------------------
        root_span = Trace.start_span(f"{request.method} {request.path}")
        request.span = root_span

        try:
            response = self.get_response(request)
            response["X-Correlation-ID"] = correlation_id
            return response

        finally:
            Trace.pop_span()
            Trace.reset_correlation_id(corr_token)
            Trace.reset_website_id(website_token)