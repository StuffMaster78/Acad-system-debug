# orders/registry/decorator.py
from __future__ import annotations

from typing import Dict, Type, List, TYPE_CHECKING, Any
import threading
import logging

log = logging.getLogger(__name__)
_lock = threading.RLock()

# Avoid importing BaseOrderAction at runtime to prevent circular imports.
# (Actions import BaseOrderAction + this decorator; base.py does NOT import this file.)
if TYPE_CHECKING:
    from orders.actions.base import BaseOrderAction  # only for type hints

_registry: Dict[str, "Type[BaseOrderAction]"] = {}


class DuplicateActionError(Exception):
    pass


def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def register_order_action(name: str):
    """
    Decorator to register an order action class by name.

    Usage:
        @register_order_action("archive_order")
        class ArchiveOrderAction(BaseOrderAction):
            ...
    """
    key = _normalize(name)
    if not key:
        raise ValueError("Action name must be non-empty")

    def decorator(cls: "Type[BaseOrderAction]"):
        with _lock:
            existing = _registry.get(key)
            # Idempotent in dev autoreload: if it's the same class, no-op.
            if existing is cls:
                return cls
            if existing and existing is not cls:
                raise DuplicateActionError(
                    f"Action '{key}' already registered by {existing.__module__}."
                )
            _registry[key] = cls
            log.debug("Registered action '%s' -> %s.%s", key, cls.__module__, cls.__name__)
        return cls

    return decorator


def get_registered_action(name: str) -> "Type[BaseOrderAction] | None":
    return _registry.get(_normalize(name))


def get_registered_action_keys() -> List[str]:
    return sorted(_registry.keys())


def get_all_registered_actions() -> Dict[str, "Type[BaseOrderAction]"]:
    return dict(_registry)


# Handy helpers (optional, but nice DX)
def instantiate_action(name: str, /, **kwargs: Any) -> "BaseOrderAction":
    cls = get_registered_action(name)
    if not cls:
        raise KeyError(f"Unknown action '{name}'")
    return cls(**kwargs)


def run_action(name: str, /, **kwargs: Any) -> Any:
    """
    Convenience: instantiate + execute.
    Expects kwargs matching your BaseOrderAction.__init__ signature
    (e.g., order_id=..., user=..., other params).
    """
    action = instantiate_action(name, **kwargs)
    return action.execute()