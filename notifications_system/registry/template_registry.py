"""
Template Registry for the Notifications System

Manages event template registrations (name-based and class-based),
supports decorator usage, and ensures thread-safe access.
"""

from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, List, Optional, Type


class TemplateRegistry:
    """
    A centralized, thread-safe registry for notification templates
    and class-based handlers, keyed by event and channel.
    """

    _templates: Dict[str, Dict[str, str]] = defaultdict(dict)
    _handlers: Dict[str, List[Type]] = defaultdict(list)
    _lock = Lock()

    @classmethod
    def register_template(
        cls, event_key: str, channel: str, template_name: str
    ) -> None:
        with cls._lock:
            cls._templates[event_key][channel] = template_name

    @classmethod
    def get_template(cls, event_key: str, channel: str) -> str:
        return cls._templates.get(event_key, {}).get(
            channel, "default_template.html"
        )

    @classmethod
    def register_handler(cls, event_key: str, handler_cls: Type) -> None:
        with cls._lock:
            cls._handlers[event_key].append(handler_cls)

    @classmethod
    def get_handlers(cls, event_key: str) -> List[Type]:
        return cls._handlers.get(event_key, [])

    # --- Decorators below ---

    @classmethod
    def template(cls, event_key: str, channel: str, template_name: str) -> Callable:
        """
        Decorator to register a template for a given event and channel.
        """
        def decorator(fn: Callable) -> Callable:
            cls.register_template(event_key, channel, template_name)
            return fn
        return decorator

    @classmethod
    def handler(cls, event_key: str) -> Callable:
        """
        Decorator to register a class-based handler for a specific event.
        """
        def decorator(template_cls: Type) -> Type:
            cls.register_handler(event_key, template_cls)
            return template_cls
        return decorator
    
    @classmethod
    def get_templates_for_event(cls, event_key: str) -> dict:
        return cls._templates.get(event_key, {})



# Optional shortcuts
register_notification_template = TemplateRegistry.register_template
get_notification_template = TemplateRegistry.get_template
register_template_handler = TemplateRegistry.register_handler
get_template_handlers = TemplateRegistry.get_handlers
