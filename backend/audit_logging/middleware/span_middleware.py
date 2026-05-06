from audit_logging.tracing.span_manager import SpanManager


class AuditSpanMiddleware:
    """
    Attaches span manager to every request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.span_manager = SpanManager()

        response = self.get_response(request)

        return response