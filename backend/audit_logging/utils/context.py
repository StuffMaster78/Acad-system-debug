from audit_logging.tracing.context import TraceContext


def get_correlation_id() -> str | None:
    return TraceContext.get_correlation_id()


def get_website_id() -> str | None:
    return TraceContext.get_website_id()