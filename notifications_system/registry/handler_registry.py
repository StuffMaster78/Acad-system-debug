# notifications_system/registry/handler_registry.py
from __future__ import annotations

import asyncio
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from typing import Callable, Dict, List, Tuple, Any, Iterable

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class HandlerSpec:
    func: Callable[..., Any]
    priority: int = 100
    once: bool = False

# Exact-key handlers: event_key -> [HandlerSpec, ...]
_HANDLERS: Dict[str, List[HandlerSpec]] = {}
# Wildcard handlers: pattern like "order.*" or "*" -> [HandlerSpec, ...]
_WILDCARD: Dict[str, List[HandlerSpec]] = {}

_LOCK = Lock()


def _sorted_append(bucket: Dict[str, List[HandlerSpec]],
                   key: str,
                   spec: HandlerSpec) -> None:
    specs = bucket.setdefault(key, [])
    # Idempotence: skip if same function already present
    if any(s.func is spec.func for s in specs):
        return
    specs.append(spec)
    specs.sort(key=lambda s: s.priority)


def register(event_key: str,
             func: Callable[..., Any],
             *,
             priority: int = 100,
             once: bool = False,
             replace: bool = False) -> None:
    """Register a handler for an event key.

    Supports wildcard keys:
      - "order.*" matches any event starting with "order."
      - "*" matches every event
    """
    spec = HandlerSpec(func=func, priority=priority, once=once)
    with _LOCK:
        if replace:
            if "*" in event_key or event_key.endswith(".*"):
                _WILDCARD[event_key] = [spec]
            else:
                _HANDLERS[event_key] = [spec]
            return

        if event_key == "*" or event_key.endswith(".*"):
            _sorted_append(_WILDCARD, event_key, spec)
        else:
            _sorted_append(_HANDLERS, event_key, spec)


def unregister(event_key: str, func: Callable[..., Any]) -> None:
    with _LOCK:
        bucket = _WILDCARD if (event_key == "*" or event_key.endswith(".*")) else _HANDLERS
        specs = bucket.get(event_key, [])
        bucket[event_key] = [s for s in specs if s.func is not func]


def get(event_key: str) -> Tuple[HandlerSpec, ...]:
    """Return exact-match handlers only (tuple snapshot)."""
    with _LOCK:
        return tuple(_HANDLERS.get(event_key, ()))


def get_all_for(event_key: str) -> Tuple[HandlerSpec, ...]:
    """Return exact + wildcard handlers applicable to this event key."""
    with _LOCK:
        exact = list(_HANDLERS.get(event_key, ()))
        wild: List[HandlerSpec] = []
        for pattern, specs in _WILDCARD.items():
            if pattern == "*" or (
                pattern.endswith(".*") and event_key.startswith(pattern[:-2] + ".")
            ):
                wild.extend(specs)
        # Merge and sort by priority (stable)
        merged = exact + wild
        merged.sort(key=lambda s: s.priority)
        return tuple(merged)


def clear() -> None:
    with _LOCK:
        _HANDLERS.clear()
        _WILDCARD.clear()


def has_handlers(event_key: str) -> bool:
    return bool(get_all_for(event_key))


def list_events() -> List[str]:
    with _LOCK:
        return sorted(_HANDLERS.keys())


def dispatch(event_key: str, *args, **kwargs) -> List[Any]:
    """
    Invoke handlers for event_key (exact + wildcard) in priority order.
    Exceptions are logged (not raised).
    Handlers marked 'once' are unregistered after successful execution.

    NOTE: async handlers are executed fire-and-forget here.
          Use dispatch_async to await async handlers.
    """
    results: List[Any] = []
    to_remove: List[tuple[str, Callable[..., Any]]] = []

    for spec in get_all_for(event_key):
        try:
            if asyncio.iscoroutinefunction(spec.func):
                # Fire-and-forget in sync path
                asyncio.get_event_loop().create_task(spec.func(*args, **kwargs))
                results.append(None)
            else:
                results.append(spec.func(*args, **kwargs))
                if spec.once:
                    # We need to know which bucket to remove from; guess based on registration shape
                    key = event_key if spec in _HANDLERS.get(event_key, []) else _wildcard_key_for(event_key, spec)
                    if key:
                        to_remove.append((key, spec.func))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Handler for '%s' crashed: %s", event_key, exc)

    for key, func in to_remove:
        unregister(key, func)

    return results


async def dispatch_async(event_key: str, *args, **kwargs) -> List[Any]:
    """
    Async-aware dispatch: awaits async handlers and runs sync handlers inline.
    Preserves 'once' semantics for successful sync handlers.
    """
    results: List[Any] = []
    to_remove: List[tuple[str, Callable[..., Any]]] = []
    coros: List[asyncio.Task] = []

    for spec in get_all_for(event_key):
        try:
            if asyncio.iscoroutinefunction(spec.func):
                coros.append(asyncio.create_task(spec.func(*args, **kwargs)))
                results.append(None)
            else:
                results.append(spec.func(*args, **kwargs))
                if spec.once:
                    key = event_key if spec in _HANDLERS.get(event_key, []) else _wildcard_key_for(event_key, spec)
                    if key:
                        to_remove.append((key, spec.func))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Handler for '%s' crashed: %s", event_key, exc)

    if coros:
        try:
            await asyncio.gather(*coros, return_exceptions=True)
        except Exception:  # just in case
            logger.exception("Async handlers gather crashed for '%s'", event_key)

    for key, func in to_remove:
        unregister(key, func)

    return results


def _wildcard_key_for(event_key: str, spec: HandlerSpec) -> str | None:
    """Find the wildcard key under which this spec is registered for event_key."""
    for pattern, specs in _WILDCARD.items():
        if spec in specs:
            if pattern == "*" or (pattern.endswith(".*") and event_key.startswith(pattern[:-2] + ".")):
                return pattern
    return None


# --- Decorator sugar ---------------------------------------------------------

def notification_handler(event_key: str, *, priority: int = 100, once: bool = False):
    """
    Usage:
        @notification_handler("order.created", priority=50)
        def my_handler(context): ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        register(event_key, func, priority=priority, once=once)
        return func
    return decorator


# --- Test helper -------------------------------------------------------------

@contextmanager
def temporary_handler(event_key: str,
                      func: Callable[..., Any],
                      *,
                      priority: int = 100,
                      once: bool = False):
    """Temporarily register a handler inside a 'with' block (useful for tests)."""
    register(event_key, func, priority=priority, once=once)
    try:
        yield
    finally:
        unregister(event_key, func)