from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Optional, Tuple, TYPE_CHECKING


# ------------------------------------------------------------
# Import Span ONLY for type checking (prevents circular issues)
# ------------------------------------------------------------

if TYPE_CHECKING:
    from audit_logging.tracing.span import Span


# ------------------------------------------------------------
# Context variables
# ------------------------------------------------------------

_correlation_id: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)

_website_id: ContextVar[str | None] = ContextVar(
    "website_id",
    default=None,
)

_span_stack: ContextVar[Tuple["Span", ...]] = ContextVar(
    "span_stack",
    default=(),
)


# ------------------------------------------------------------
# TraceContext
# ------------------------------------------------------------

class TraceContext:
    """
    Runtime request tracing context.

    Holds ONLY:
    - correlation_id
    - website_id (tenant)
    - span stack (execution tracing)
    """

    # -------------------------
    # Correlation ID
    # -------------------------

    @staticmethod
    def set_correlation_id(cid: str):
        return _correlation_id.set(cid)

    @staticmethod
    def get_correlation_id() -> str | None:
        return _correlation_id.get()

    @staticmethod
    def reset_correlation_id(token) -> None:
        _correlation_id.reset(token)

    # -------------------------
    # Website / tenant
    # -------------------------

    @staticmethod
    def set_website_id(wid: str | None):
        return _website_id.set(wid)

    @staticmethod
    def get_website_id() -> str | None:
        return _website_id.get()

    @staticmethod
    def reset_website_id(token) -> None:
        _website_id.reset(token)

    # -------------------------
    # Span stack
    # -------------------------

    @staticmethod
    def push_span(span: "Span") -> None:
        stack = _span_stack.get()
        _span_stack.set(stack + (span,))

    @staticmethod
    def pop_span() -> "Span | None":
        stack = _span_stack.get()

        if not stack:
            return None

        span = stack[-1]
        _span_stack.set(stack[:-1])
        return span

    @staticmethod
    def current_span() -> "Span | None":
        stack = _span_stack.get()
        return stack[-1] if stack else None

    @staticmethod
    def depth() -> int:
        return len(_span_stack.get())

    # -------------------------
    # Snapshot
    # -------------------------

    @staticmethod
    def snapshot() -> dict:
        return {
            "correlation_id": _correlation_id.get(),
            "website_id": _website_id.get(),
            "span": TraceContext.current_span(),
        }

    # -------------------------
    # Utilities
    # -------------------------

    @staticmethod
    def new_correlation_id() -> str:
        return str(uuid.uuid4())