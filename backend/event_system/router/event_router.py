from __future__ import annotations

import logging
from collections.abc import Callable

from event_system.models.event_outbox import EventOutbox

logger = logging.getLogger(__name__)

EventHandler = Callable[[EventOutbox], object | None]


class EventRouter:
    """
    Deterministic 1:1 event routing registry.
    """

    _routes: dict[str, EventHandler] = {}

    @classmethod
    def register(cls, event_type: str, handler: EventHandler) -> None:
        if isinstance(handler, list):
            raise TypeError(
                f"Invalid handler for {event_type}: list[str] detected"
            )

        if not callable(handler):
            raise TypeError(
                f"Handler for {event_type} must be callable"
            )

        cls._routes[event_type] = handler

    @classmethod
    def get(cls, event_type: str) -> EventHandler | None:
        handler = cls._routes.get(event_type)

        if isinstance(handler, list):
            raise TypeError(
                f"Corrupted registry: list[str] stored for {event_type}"
            )

        return handler