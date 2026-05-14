from collections.abc import Callable

from event_system.models.event_outbox import EventOutbox


class EventRouter:
    """
    Simple handler registry.
    No execution logic here anymore.
    """

    _routes: dict[str, Callable[[EventOutbox], None]] = {}

    @classmethod
    def register(cls, event_type: str, handler: Callable[[EventOutbox], None]) -> None:
        cls._routes[event_type] = handler

    @classmethod
    def get(cls, event_type: str) -> Callable[[EventOutbox], None] | None:
        return cls._routes.get(event_type)