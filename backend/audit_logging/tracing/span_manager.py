from typing import Dict
from audit_logging.tracing.span import AuditSpan


class SpanManager:
    """
    Holds active spans per request lifecycle.
    """

    def __init__(self):
        self._spans: Dict[str, AuditSpan] = {}

    def start_span(self, name: str, correlation_id: str) -> AuditSpan:
        span = AuditSpan(name=name, correlation_id=correlation_id).start()
        self._spans[str(span.span_id)] = span
        return span

    def finish_span(self, span_id: str) -> AuditSpan | None:
        span = self._spans.get(str(span_id))
        if not span:
            return None

        span.finish()
        return span