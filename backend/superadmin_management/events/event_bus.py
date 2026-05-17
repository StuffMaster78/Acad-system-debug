import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventBus:
    _handlers = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: type, handler):
        cls._handlers[event_type].append(handler)

    @classmethod
    def publish(cls, event):
        handlers = cls._handlers.get(type(event), [])

        if not handlers:
            logger.warning("No handlers for event=%s", type(event).__name__)
            return

        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.exception("Handler failed: %s", exc)