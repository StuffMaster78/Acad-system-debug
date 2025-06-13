"""
Registry for order action classes with auto-discovery support.
"""

import importlib
import inspect
import warnings
from typing import Type, Dict
import pkgutil

from orders.actions.base import BaseOrderAction

_registry: Dict[str, Type[BaseOrderAction]] = {}

EXCLUDE_MODULES = {
    '__init__', 'base', 'registry', 'dispatcher', '__pycache__'
}


def register_action(action_name: str, action_class: Type[BaseOrderAction]):
    """
    Register an action class under a unique action_name.
    """
    if action_name in _registry:
        raise ValueError(f"Action '{action_name}' already registered.")
    _registry[action_name] = action_class


def get_action_class(action_name: str) -> Type[BaseOrderAction]:
    """
    Retrieve the action class registered under action_name.
    """
    if action_name not in _registry:
        raise KeyError(f"No action registered under '{action_name}'.")
    return _registry[action_name]


def all_actions() -> Dict[str, Type[BaseOrderAction]]:
    """
    Return a copy of all registered actions.
    """
    return dict(_registry)


def _to_snake_case(name: str) -> str:
    import re
    # Convert CamelCase to snake_case (UnpaidOrderAction -> unpaid_order_action)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def auto_discover_actions():
    """
    Automatically discover and register all BaseOrderAction subclasses
    from each Python file in the `orders.actions` package (excluding some).
    """
    import orders.actions
    package = orders.actions
    prefix = package.__name__ + "."

    # Scan all modules in orders.actions folder
    for finder, module_name, ispkg in pkgutil.iter_modules(
        package.__path__, prefix
    ):
        short_name = module_name.rsplit('.', 1)[-1]
        if short_name in EXCLUDE_MODULES:
            continue

        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BaseOrderAction)
                and obj is not BaseOrderAction
            ):
                if not hasattr(obj, 'action_name'):
                    generated_name = _to_snake_case(name)
                    warnings.warn(
                        f"Action class '{name}' missing 'action_name', "
                        f"auto-generated '{generated_name}'. It's better to "
                        f"define it explicitly.",
                        stacklevel=2,
                    )
                    setattr(obj, 'action_name', generated_name)

                if not hasattr(obj, 'action_name'):
                    raise AttributeError(
                        f"Action class '{name}' must define an 'action_name'."
                    )

                register_action(obj.action_name, obj)