from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path
import threading
from threading import Lock
from typing import Callable, Dict, List, Tuple, Type

from django.apps import apps
from django.utils.module_loading import autodiscover_modules

logger = logging.getLogger(__name__)

# =========================
# Base class (class-based)
# =========================

class BaseNotificationTemplate:
    """Minimal base for class-based templates.

    Subclasses should set ``event_name`` to a canonical event key and
    override :meth:`render`. The service treats the class template as the
    source of truth for title/text/html.

    Attributes:
        event_name: The canonical event key.
        context: Optional default context merged into render-time context.
    """

    event_name: str = "generic"

    def __init__(self, context: Dict | None = None):
        self.context = context or {}

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        """Render title, text, and HTML.

        Args:
            context: Extra context merged with ``self.context``.

        Returns:
            (title, text, html) tuple.
        """
        ctx = {**self.context, **(context or {})}
        title = ctx.get("title", "No Title")
        text = ctx.get("message", "")
        html = f"<strong>{title}</strong><br>{text}"
        return title, text, html


# =====================================
# Registry (both class- and name-based)
# =====================================

# Class-based templates: event_key -> TemplateClass
_TEMPLATE_CLASSES: Dict[str, Type[BaseNotificationTemplate]] = {}

# Name-based templates: event_key -> {channel: template_name}
_TEMPLATE_NAMES: Dict[str, Dict[str, str]] = {}

# Optional class-based handlers tied to events
_HANDLERS: Dict[str, List[Type]] = {}

_LOCK = threading.RLock()
_AUTOLOADED = False


# ---------------
# Class-based API
# ---------------

def register_template_class(
    event_key: str,
) -> Callable[[Type[BaseNotificationTemplate]],
              Type[BaseNotificationTemplate]]:
    """Decorator to register a class-based template for an event key.

    Args:
        event_key: Canonical event key.

    Returns:
        Decorator that registers the class.
    """
    def _decorator(cls: Type[BaseNotificationTemplate]
                   ) -> Type[BaseNotificationTemplate]:
        with _LOCK:
            existing = _TEMPLATE_CLASSES.get(event_key)
            if existing and existing is not cls:
                # Use debug level instead of warning for template overwrites
                logger.debug(
                    "Template for '%s' already registered with %s; "
                    "overwriting with %s",
                    event_key,
                    getattr(existing, "__name__", existing),
                    cls.__name__,
                )
            _TEMPLATE_CLASSES[event_key] = cls
        logger.debug(
            "Registered template class for '%s': %s",
            event_key,
            cls.__name__,
        )
        return cls
    return _decorator


def get_template(event_key: str) -> BaseNotificationTemplate:
    """Return an instance of the template for the given event key.

    If no class is registered, returns a BaseNotificationTemplate.
    Autoloads templates on first access.

    Args:
        event_key: Canonical event key.

    Returns:
        Instance of a template class.
    """
    ensure_autoload()
    with _LOCK:
        cls = _TEMPLATE_CLASSES.get(event_key, BaseNotificationTemplate)
    return cls()


def template_class(
    event_key: str,
) -> Callable[[Type[BaseNotificationTemplate]],
              Type[BaseNotificationTemplate]]:
    """Alias of register_template_class for ergonomic imports."""
    return register_template_class(event_key)


# --------------------------------------------
# Name-based (per-channel) filename API (kept)
# --------------------------------------------

def register_template_name(event_key: str, channel: str,
                           template_name: str) -> None:
    """Register a template filename for (event_key, channel)."""
    with _LOCK:
        _TEMPLATE_NAMES.setdefault(event_key, {})[channel] = template_name
    logger.debug(
        "Registered template name for '%s' [%s] -> %s",
        event_key,
        channel,
        template_name,
    )


def get_template_name(event_key: str, channel: str) -> str:
    """Get the template filename for (event_key, channel).

    Returns:
        Registered name or 'default_template.html' if none.
    """
    with _LOCK:
        return _TEMPLATE_NAMES.get(event_key, {}).get(
            channel, "default_template.html"
        )


# ------------------
# Optional handlers
# ------------------

def register_handler(event_key: str) -> Callable[[Type], Type]:
    """Decorator to register a class handler for an event key."""
    def _decorator(cls: Type) -> Type:
        with _LOCK:
            _HANDLERS.setdefault(event_key, []).append(cls)
        logger.debug(
            "Registered handler for '%s': %s", event_key, cls.__name__
        )
        return cls
    return _decorator


def get_handlers(event_key: str) -> List[Type]:
    """Return a list of handler classes for the event key."""
    with _LOCK:
        return list(_HANDLERS.get(event_key, []))


# ---------------
# Autoload logic
# ---------------

def _autoload_central() -> None:
    """Import notifications_system.template_list.* so decorators run."""
    try:
        import notifications_system.template_list as pkg
    except Exception as exc:  # noqa: BLE001
        logger.debug("No central template_list package found: %s", exc)
        return

    pkg_path = Path(pkg.__file__).parent
    for _, mod_name, is_pkg in pkgutil.iter_modules([str(pkg_path)]):
        if is_pkg:
            continue
        full = f"{pkg.__name__}.{mod_name}"
        try:
            importlib.import_module(full)
            logger.debug("Loaded central template module: %s", full)
        except Exception as exc:  # noqa: BLE001
            # Use debug level instead of warning - template imports are optional
            logger.debug("Failed to import %s: %s", full, exc)


def _autoload_per_app() -> None:
    """Import <app>.notification_templates across installed apps."""
    try:
        autodiscover_modules("notification_templates")
        logger.debug("Autodiscovered per-app notification_templates.")
    except Exception as exc:  # noqa: BLE001
        # Use debug level instead of warning - autodiscovery failures are non-critical
        logger.debug("autodiscover(notification_templates) failed: %s", exc)

    for app_cfg in apps.get_app_configs():
        mod = f"{app_cfg.name}.notification_templates"
        try:
            importlib.import_module(mod)
            logger.debug("Loaded per-app templates: %s", mod)
        except ModuleNotFoundError:
            continue
        except Exception as exc:  # noqa: BLE001
            # Use debug level instead of warning - template imports are optional
            logger.debug("Failed to import %s: %s", mod, exc)


def autoload_all_templates() -> None:
    """Load central + per-app templates (idempotent)."""
    with _LOCK:
        global _AUTOLOADED
        if _AUTOLOADED:
            return
        _autoload_central()
        _autoload_per_app()
        _TEMPLATE_CLASSES.setdefault("generic", BaseNotificationTemplate)
        _AUTOLOADED = True
    logger.debug(
        "Template autoload complete; %d class templates; %d name mappings.",
        len(_TEMPLATE_CLASSES),
        sum(len(v) for v in _TEMPLATE_NAMES.values()),
    )


def ensure_autoload() -> None:
    """Autoload templates if not yet loaded (thread-safe)."""
    if not _AUTOLOADED:
        autoload_all_templates()


# -----------------------------
# Back-compat: register_template
# -----------------------------

def register_template(*args, **kwargs):
    """Back-compat shim for older decorator/call styles.

    Supports:
        1) @register_template("event.key")  -> class-based decorator
        2) @register_template               -> class with .event_name
        3) register_template(event_key="..",
                             channel="..",
                             template_name="..")
        4) register_template("event.key", "channel", "template.html")

    Raises:
        TypeError: If called with an unsupported signature.
    """
    # Case 1: @register_template("event.key")
    if len(args) == 1 and isinstance(args[0], str) and not kwargs:
        event_key = args[0]

        def _decorator(cls: Type[BaseNotificationTemplate]):
            register_template_class(event_key)(cls)
            return cls

        return _decorator

    # Case 2: bare @register_template on a class
    if (len(args) == 1 and isinstance(args[0], type)
            and issubclass(args[0], BaseNotificationTemplate)):
        cls = args[0]
        event_key = getattr(cls, "event_name", None)
        if not event_key or not isinstance(event_key, str):
            raise TypeError(
                "Bare @register_template requires "
                "class.event_name = 'event.key'"
            )
        register_template_class(event_key)(cls)
        return cls

    # Case 3: kwargs name-based
    required = {"event_key", "channel", "template_name"}
    if not args and required <= set(kwargs):
        ek = kwargs["event_key"]
        ch = kwargs["channel"]
        tn = kwargs["template_name"]
        register_template_name(ek, ch, tn)

        def _decorator(obj):
            return obj

        return _decorator

    # Case 4: positional name-based
    if len(args) == 3 and all(isinstance(a, str) for a in args) and not kwargs:
        ek, ch, tn = args
        register_template_name(ek, ch, tn)

        def _decorator(obj):
            return obj

        return _decorator

    raise TypeError(
        "register_template usage:\n"
        "  @register_template('event.key')\n"
        "  @register_template  # with class.event_name = 'event.key'\n"
        "  register_template(event_key='..', channel='..', "
        "template_name='..')\n"
        "  register_template('event.key','channel','template.html')"
    )


# ----------
# Utilities
# ----------

def get_templates_for_event(event_key: str) -> Dict[str, str]:
    """Return channel->template_name mapping for an event key."""
    with _LOCK:
        return dict(_TEMPLATE_NAMES.get(event_key, {}))


# -----------
# Test hooks
# -----------

def clear_registry() -> None:
    """Clear all registered templates/handlers (tests only)."""
    with _LOCK:
        _TEMPLATE_CLASSES.clear()
        _TEMPLATE_NAMES.clear()
        _HANDLERS.clear()
        global _AUTOLOADED
        _AUTOLOADED = False


__all__ = [
    "BaseNotificationTemplate",
    "register_template_class",
    "template_class",
    "register_template",
    "get_template",
    "get_template_name",
    "register_template_name",
    "get_templates_for_event",
    "register_handler",
    "get_handlers",
    "autoload_all_templates",
    "ensure_autoload",
    "clear_registry",
]