from audit_logging.tracing.trace import Trace


def inject_trace(task_kwargs, correlation_id, span=None):
    task_kwargs["correlation_id"] = correlation_id
    if span:
        task_kwargs["span_id"] = str(span.span_id)
    return task_kwargs


def restore_trace(correlation_id=None, span_id=None):
    if correlation_id:
        Trace.set_correlation_id(correlation_id)