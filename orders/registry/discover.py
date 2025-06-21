import importlib
import pkgutil
import inspect
import logging

from orders.actions.base import BaseOrderAction

logger = logging.getLogger(__name__)

def auto_discover_order_actions():
    """
    Auto-discover and import all order action classes in the actions module.
    This triggers the decorators to register them in the registry.
    """
    from orders.registry.decorator import register_order_action  # safe import

    import orders.actions  # This triggers __path__ access

    for _, module_name, is_pkg in pkgutil.iter_modules(orders.actions.__path__):
        if module_name.startswith("_") or is_pkg:
            continue
        module_path = f"orders.actions.{module_name}"
        try:
            module = importlib.import_module(module_path)
            found = False
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BaseOrderAction) and cls is not BaseOrderAction:
                    found = True
            if not found:
                logger.warning(f"[actions] {module_path} loaded but no valid actions found.")
        except Exception as e:
            logger.exception(f"Failed to import action module: {module_path}")