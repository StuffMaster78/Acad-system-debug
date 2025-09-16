# notifications_system/services/templates_registry.py
"""
DEPRECATED: import from notifications_system.registry.template_registry instead.

This module will be removed. Search & replace:
  from notifications_system.services.templates_registry import ...
→ from notifications_system.registry.template_registry import ...
"""

from __future__ import annotations
import warnings

warnings.warn(
    "notifications_system.services.templates_registry is deprecated. "
    "Use notifications_system.registry.template_registry instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export only. No logic here.
from notifications_system.registry.template_registry import (  # noqa: F401
    BaseNotificationTemplate,
    register_template_class as register_template,  # legacy alias
    template_class,
    get_template,
    autoload_all_templates,
    register_template_name,
    get_template_name,
    register_handler,   # if you still use handlers
    get_handlers,
    get_templates_for_event,
)

__all__ = [
    "BaseNotificationTemplate",
    "register_template",
    "template_class",
    "get_template",
    "autoload_all_templates",
    "register_template_name",
    "get_template_name",
    "register_handler",
    "get_handlers",
    "get_templates_for_event",
]
