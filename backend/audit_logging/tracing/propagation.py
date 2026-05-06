class TracePropagation:

    @staticmethod
    def inject(headers: dict, correlation_id: str, span_id=None):
        headers["X-Correlation-ID"] = correlation_id
        if span_id:
            headers["X-Span-ID"] = str(span_id)
        return headers

    @staticmethod
    def extract(headers: dict):
        return {
            "correlation_id": headers.get("X-Correlation-ID"),
            "span_id": headers.get("X-Span-ID"),
        }