from __future__ import annotations
from typing import Callable, Any
from .registry.handler_registry import register as _register

def notification_handler(event_type: str, *, priority: int = 100, once: bool = False, replace: bool = False):
    """
    Register a function to handle a notification event.

    Args:
        event_type: canonical event key (e.g., "order.created")
        priority: lower runs earlier (default 100)
        once: remove handler after first successful call
        replace: replace all existing handlers for this event with this one
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _register(event_type, func, priority=priority, once=once, replace=replace)
        return func
    return decorator
