from collections.abc import Callable

EventHandler = Callable[..., None]


class EventRegistry:
    """
    Central registry for all domain event handlers.
    """

    _routes: dict[str, EventHandler] = {}

    @classmethod
    def register(cls, event_type: str, handler: EventHandler) -> None:
        if not callable(handler):
            raise TypeError(f"Handler must be callable for {event_type}")

        cls._routes[event_type] = handler

    @classmethod
    def get(cls, event_type: str) -> EventHandler | None:
        return cls._routes.get(event_type)