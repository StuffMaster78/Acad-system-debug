from __future__ import annotations

import time
import uuid
from contextvars import ContextVar
from typing import Optional

from audit_logging.tracing.span import Span


# -------------------------
# Context state
# -------------------------

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_website_id: ContextVar[str | None] = ContextVar("website_id", default=None)
_span_stack: ContextVar[tuple[Span, ...]] = ContextVar("span_stack", default=())


# -------------------------
# Trace (single authority)
# -------------------------

class Trace:
    """
    The ONLY tracing system.

    Responsibilities:
    - correlation tracking
    - tenant context (read-only)
    - span lifecycle
    - snapshot creation
    """

    # -------------------------
    # Correlation
    # -------------------------

    @staticmethod
    def set_correlation_id(cid: str):
        return _correlation_id.set(cid)

    @staticmethod
    def get_correlation_id() -> str | None:
        return _correlation_id.get()

    # -------------------------
    # Tenant (READ ONLY here)
    # -------------------------

    @staticmethod
    def set_website_id(wid: str):
        return _website_id.set(wid)

    @staticmethod
    def get_website_id() -> str | None:
        return _website_id.get()

    # -------------------------
    # Span lifecycle
    # -------------------------

    @staticmethod
    def current_span() -> Span | None:
        stack = _span_stack.get()
        return stack[-1] if stack else None

    @staticmethod
    def push_span(span: Span) -> Span:
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
    def reset_correlation_id(token):
        _correlation_id.reset(token)

    @staticmethod
    def reset_website_id(token):
        _website_id.reset(token)
    # -------------------------
    # Span factory (ONLY WAY TO CREATE SPANS)
    # -------------------------

    @staticmethod
    def start_span(name: str) -> Span:
        parent = Trace.current_span()

        span = Span(
            name=name,
            span_id=uuid.uuid4().hex,
            parent_id=getattr(parent, "span_id", None),
            start_time=time.time(),
        )

        Trace.push_span(span)
        return span

    # -------------------------
    # Snapshot (single export contract)
    # -------------------------

    @staticmethod
    def snapshot() -> dict:
        span = Trace.current_span()

        return {
            "correlation_id": Trace.get_correlation_id(),
            "website_id": Trace.get_website_id(),
            "span": span,
            "span_id": getattr(span, "span_id", None) if span else None,
            "parent_span_id": getattr(span, "parent_id", None) if span else None,
        }