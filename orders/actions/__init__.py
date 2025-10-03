import importlib
import pkgutil
import logging

log = logging.getLogger(__name__)
_SKIP = {"__init__", "base", "registry", "discover", "helpers"}

def autodiscover() -> list[str]:
    loaded: list[str] = []
    pkg = __name__  # "orders.actions"
    for _, modname, ispkg in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if ispkg or modname in _SKIP or modname.startswith("_"):
            continue
        try:
            importlib.import_module(f"{pkg}.{modname}")
            loaded.append(modname)
        except Exception as exc:
            log.warning("[actions] failed to import %s: %s", modname, exc, exc_info=True)
    return loaded