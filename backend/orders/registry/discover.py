from __future__ import annotations

import importlib
import pkgutil
import inspect
import logging
from types import ModuleType
from typing import Set, Tuple

logger = logging.getLogger(__name__)

def _iter_action_modules(pkg: ModuleType) -> Tuple[str, ...]:
    """
    Yield fully-qualified module names under the given package,
    recursively (skips private/dunder and tests).
    """
    pkg_name = pkg.__name__
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg_name + "."):
        name = m.name
        # skip private modules/packages and tests
        base = name.rsplit(".", 1)[-1]
        if base.startswith("_") or base.startswith("test"):
            continue
        yield name

def _is_action_class(obj, base_cls) -> bool:
    try:
        return inspect.isclass(obj) and issubclass(obj, base_cls) and obj is not base_cls
    except Exception:
        # Not all class-like objects are safe to issubclass()
        return False

# cache to avoid noisy re-import logs under autoreload
_IMPORTED_MODULES: Set[str] = set()

def auto_discover_order_actions() -> int:
    """
    Recursively import all action modules so that @register_order_action
    runs at import time. Returns number of *classes* discovered.
    """
    try:
        import orders.actions as actions_pkg
        from orders.actions.base import BaseOrderAction  # import here to dodge cycles
    except Exception as exc:
        logger.exception("[actions] Failed to import actions package/base: %s", exc)
        return 0

    discovered_classes = 0
    for module_name in _iter_action_modules(actions_pkg):
        try:
            # Avoid double-import logs during dev reloads
            first_import = module_name not in _IMPORTED_MODULES
            module = importlib.import_module(module_name)
            _IMPORTED_MODULES.add(module_name)

            found_any = False
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if _is_action_class(cls, BaseOrderAction):
                    found_any = True
                    discovered_classes += 1

            if first_import and not found_any:
                logger.debug("[actions] %s imported; no BaseOrderAction subclasses found.", module_name)

        except Exception as exc:
            logger.exception("[actions] Failed to import module %s: %s", module_name, exc)

    logger.info("[actions] auto-discovered %d action classes.", discovered_classes)
    return discovered_classes