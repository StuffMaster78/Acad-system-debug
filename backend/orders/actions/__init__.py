import importlib
import logging

log = logging.getLogger(__name__)

CURRENT_ACTION_MODULES = (
    "status_transition",
    "transition_to_pending",
)


def autodiscover() -> list[str]:
    loaded: list[str] = []
    pkg = __name__ # "orders.actions"
    for modname in CURRENT_ACTION_MODULES:
        try:
            importlib.import_module(f"{pkg}.{modname}")
            loaded.append(modname)
        except Exception as exc:
            log.exception("[actions] failed to import current action %s: %s", modname, exc)
    return loaded
