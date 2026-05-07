import uuid
import time
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional


# -------------------------
# Context Vars
# -------------------------

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_website_id: ContextVar[str | None] = ContextVar("website_id", default=None)
_website_locked: ContextVar[bool] = ContextVar("website_locked", default=False)
_span_stack: ContextVar[tuple["Span", ...]] = ContextVar("span_stack", default=())


# -------------------------
# Span
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


# -------------------------
# Trace (single authority)
# -------------------------

class Trace:

    # -------------------------
    # Correlation
    # -------------------------
    @staticmethod
    def set_correlation_id(cid: str):
        return _correlation_id.set(cid)

    @staticmethod
    def get_correlation_id() -> str | None:
        return _correlation_id.get()

    @staticmethod
    def reset_correlation_id(token):
        _correlation_id.reset(token)

    # -------------------------
    # Tenant (website)
    # -------------------------
    @staticmethod
    def set_website_id(wid: str):
        if not wid:
            raise RuntimeError("website_id cannot be empty")
        return _website_id.set(wid)

    @staticmethod
    def get_website_id() -> str:
        wid = _website_id.get()
        if not wid:
            raise RuntimeError("Missing tenant context (website_id)")
        return wid

    @staticmethod
    def reset_website_id(token):
        _website_id.reset(token)

    # -------------------------
    # Span lifecycle
    # -------------------------
    @staticmethod
    def current_span() -> Span | None:
        stack = _span_stack.get()
        return stack[-1] if stack else None

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
    def depth() -> int:
        return len(_span_stack.get())

    # -------------------------
    # Span factory (single entry point)
    # -------------------------
    @staticmethod
    def start_span(name: str) -> Span:
        parent = Trace.current_span()

        span = Span(
            name=name,
            span_id=str(uuid.uuid4()),
            parent_id=getattr(parent, "span_id", None),
            start_time=time.time(),
        )

        Trace.push_span(span)
        return span

    @staticmethod
    def finish_span(span: Span) -> Span:
        span.finish()

        # ensure stack consistency
        current = Trace.current_span()
        if current and current.span_id == span.span_id:
            Trace.pop_span()

        return span
    


    @staticmethod
    def snapshot():
        """
        Single source snapshot for audit/logging systems.
        """
        span = Trace.current_span()

        return {
            "correlation_id": Trace.get_correlation_id(),
            "website_id": Trace.get_website_id(),
            "span": span,
            "span_id": getattr(span, "span_id", None) if span else None,
            "span_name": getattr(span, "name", None) if span else None,
            "parent_span_id": getattr(span, "parent_id", None) if span else None,
        }
    


class TraceContext:

    # -------------------------
    # WEBSITE (TENANT) CONTROL
    # -------------------------
    @staticmethod
    def set_website_id(wid: str | None, *, force: bool = False):
        """
        Tenant setter with immutability guarantee.
        """

        locked = _website_locked.get()

        # already locked → ignore or fail
        if locked and not force:
            return _website_id.get()

        token = _website_id.set(wid)

        # lock immediately after first valid set
        if wid is not None:
            _website_locked.set(True)

        return token

    @staticmethod
    def get_website_id() -> str | None:
        return _website_id.get()

    @staticmethod
    def reset_website_id(token, *, force: bool = False):
        """
        Reset only allowed if explicitly forced (middleware teardown).
        """
        if _website_locked.get() and not force:
            return

        _website_id.reset(token)
        _website_locked.set(False)