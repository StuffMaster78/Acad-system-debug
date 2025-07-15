
import importlib
import pkgutil
import logging
from typing import Dict, Callable, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

TEMPLATE_REGISTRY: Dict[str, Callable] = {}


class BaseNotificationTemplate:
    event_name = "generic"

    def __init__(self, context=None):
        self.context = context or {}

    def render(self) -> Tuple[str, str, str]:
        title = self.context.get("title", "No Title")
        message = self.context.get("message", "")
        html_message = f"<strong>{title}</strong><br>{message}"
        return title, message, html_message


def register_template(template_cls):
    if not hasattr(template_cls, "event_name"):
        raise ValueError(
            "Template class must define an 'event_name' attribute."
        )
    TEMPLATE_REGISTRY[template_cls.event_name] = template_cls
    logger.debug(f"Registered template: {template_cls.event_name}")
    return template_cls


def get_template(event_name: str) -> BaseNotificationTemplate:
    template_cls = TEMPLATE_REGISTRY.get(event_name)
    if not template_cls:
        logger.warning(f"No template for event '{event_name}'. Using fallback.")
        template_cls = TEMPLATE_REGISTRY.get(
            "generic", BaseNotificationTemplate
        )
    return template_cls()


def load_all_templates():
    """
    Auto-imports all Python modules in the `templates` package so decorators execute.
    """
    import notifications_system.template_list
    package = notifications_system.template_list

    package_path = Path(package.__file__).parent

    for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
        if not is_pkg:
            full_module_name = f"{package.__name__}.{module_name}"
            try:
                importlib.import_module(full_module_name)
                logger.debug(
                    f"Auto-loaded template module: {full_module_name}"
                )
            except Exception as e:
                logger.warning(f"Failed to load {full_module_name}: {e}")