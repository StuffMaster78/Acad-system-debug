import uuid
from audit_logging.tracing.context import TraceContext


class CorrelationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # store in request (for external access)
        request.correlation_id = cid

        # store in trace context (internal system access)
        TraceContext.set_correlation_id(cid)

        response = self.get_response(request)

        response["X-Correlation-ID"] = cid
        return response