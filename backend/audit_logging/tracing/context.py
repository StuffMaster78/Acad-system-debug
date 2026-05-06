import uuid
import time
from contextvars import ContextVar
from dataclasses import dataclass

# -------------------------
# Context Vars
# -------------------------

_correlation_id: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)

_span_stack: ContextVar[tuple["Span", ...]] = ContextVar(
    "span_stack",
    default=(),
)

_website_id: ContextVar[str | None] = ContextVar(
    "website_id",
    default=None,
)

# -------------------------
# Span model
# -------------------------

@dataclass
class Span:
    name: str
    span_id: str
    parent_id: str | None
    start_time: float
    end_time: float | None = None

    def finish(self) -> None:
        self.end_time = time.time()

    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

@dataclass
class TraceState:
    correlation_id: str | None
    span: Span | None
    website_id: str | None

# -------------------------
# TraceContext (V1 frozen)
# -------------------------

class TraceContext:

    # correlation
    @staticmethod
    def set_correlation_id(cid: str):
        return _correlation_id.set(cid)

    @staticmethod
    def get_correlation_id() -> str | None:
        return _correlation_id.get()

    @staticmethod
    def reset_correlation_id(token):
        _correlation_id.reset(token)

    # span stack
    @staticmethod
    def push_span(span: Span):
        stack = _span_stack.get()
        _span_stack.set(stack + (span,))
        return span

    @staticmethod
    def pop_span() -> Span | None:
        stack = _span_stack.get()
        if not stack:
            return None

        span = stack[-1]
        span.finish()
        _span_stack.set(stack[:-1])
        return span

    @staticmethod
    def current_span() -> Span | None:
        stack = _span_stack.get()
        return stack[-1] if stack else None

    @staticmethod
    def depth() -> int:
        return len(_span_stack.get())

    # span factory
    @staticmethod
    def create_root_span(name: str) -> Span:
        return Span(
            name=name,
            span_id=str(uuid.uuid4()),
            parent_id=None,
            start_time=time.time(),
        )

    @staticmethod
    def create_span(name: str) -> Span:
        parent = TraceContext.current_span()
        return Span(
            name=name,
            span_id=str(uuid.uuid4()),
            parent_id=getattr(parent, "span_id", None),
            start_time=time.time(),
        )

    # unified snapshot
    @staticmethod
    def current():
        span = TraceContext.current_span()

        class TraceState:
            def __init__(self, correlation_id, span, website_id):
                self.correlation_id = correlation_id
                self.span = span
                self.website_id = website_id

        return TraceState(
            correlation_id=_correlation_id.get(),
            span=span,
            website_id=_website_id.get(),
        )
    
    @staticmethod
    def set_website_id(wid: str | None):
        return _website_id.set(wid)

    @staticmethod
    def get_website_id() -> str | None:
        return _website_id.get()

    @staticmethod
    def reset_website_id(token):
        _website_id.reset(token)