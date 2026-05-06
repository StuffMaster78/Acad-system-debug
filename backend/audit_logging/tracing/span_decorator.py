import functools
from audit_logging.tracing.context import TraceContext


def traced_span(name: str):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            span = TraceContext.create_span(name)
            TraceContext.push_span(span)

            try:
                return func(*args, **kwargs)
            finally:
                TraceContext.pop_span()

        return wrapper

    return decorator