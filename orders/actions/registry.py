"""
Registry for order action classes with auto-discovery support.
"""

_registry = {}

def register_action(action_name: str, action_class):
    """
    Register an action class under a name.
    """
    if action_name in _registry:
        raise ValueError(f"Action '{action_name}' already registered.")
    _registry[action_name] = action_class

def get_action_class(action_name: str):
    """
    Retrieve the action class registered under action_name.
    """
    return _registry.get(action_name)

def all_actions():
    """
    Return a copy of the registered actions.
    """
    return dict(_registry)

def auto_discover_actions():
    """
    Automatically discover and register all BaseOrderAction subclasses.
    """
    import importlib
    import inspect

    from orders.actions.base import BaseOrderAction

    try:
        module = importlib.import_module('orders.actions.orders_actions')
    except ModuleNotFoundError as e:
        raise ImportError("orders.actions.orders_actions could not be imported") from e

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseOrderAction) and obj is not BaseOrderAction:
            if not hasattr(obj, 'action_name'):
                raise AttributeError(f"Action class '{name}' must define an 'action_name'.")
            register_action(obj.action_name, obj)
