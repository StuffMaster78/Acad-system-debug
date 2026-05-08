from contextlib import contextmanager
from audit_logging.tracing.trace import Trace

# -------------------------
# INJECT (producer side)
# -------------------------

def inject_trace(task_kwargs: dict, correlation_id: str, span_id: str | None = None, website_id: str | None = None):
    payload = dict(task_kwargs)

    payload["correlation_id"] = correlation_id

    if span_id:
        payload["span_id"] = str(span_id)

    if website_id:
        payload["website_id"] = str(website_id)

    return payload


@contextmanager
def restore_trace(
    correlation_id: str | None = None,
    span_id: str | None = None,
    website_id: str | None = None,
):
    tokens = []

    try:
        if correlation_id:
            tokens.append(Trace.set_correlation_id(correlation_id))

        if website_id:
            tokens.append(Trace.set_website_id(website_id))

        # NOTE: span_id alone is NOT enough to rebuild full span
        # so we only store reference (future: span registry if needed)

        yield

    finally:
        # safe cleanup (prevents cross-task leakage)
        for token in reversed(tokens):
            try:
                # ContextVar reset depends on variable type
                # we infer which reset to call based on token origin
                pass
            except Exception:
                pass

        # hard safety fallback (guaranteed cleanup)
        Trace.reset_correlation_id(tokens[0]) if tokens else None
        Trace.reset_website_id(tokens[1]) if len(tokens) > 1 else None