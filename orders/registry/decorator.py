from typing import Type, Dict
from orders.actions.base import BaseOrderAction

_registry: Dict[str, Type[BaseOrderAction]] = {}

def register_order_action(name: str):
    """
    Decorator to register an order action class by name.
    Usage:
        @register_order_action("archive_order")
        class ArchiveOrderAction(BaseOrderAction):
            ...
    """
    def decorator(cls):
        if name in _registry:
            raise ValueError(f"Action '{name}' already registered.")
        _registry[name] = cls
        return cls
    return decorator

def get_registered_action(name: str) -> Type[BaseOrderAction] | None:
    """
    Retrieve a registered order action by name.
    Args:
        name (str): The name of the registered action.
    Returns:
        Type[BaseOrderAction] | None: The action class if found, otherwise None.
    """
    return _registry.get(name)

def get_all_registered_actions() -> Dict[str, Type[BaseOrderAction]]:
    """
    Retrieve all registered order actions.
    Returns:
        Dict[str, Type[BaseOrderAction]]: A copy of the registry containing all registered actions.
    """
    return _registry.copy() 