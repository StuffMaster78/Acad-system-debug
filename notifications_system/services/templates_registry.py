# notifications_system/services/templates_registry.py
"""
DEPRECATED: import from notifications_system.registry.template_registry instead.

This module will be removed. Search & replace:
  from notifications_system.services.templates_registry import ...
→ from notifications_system.registry.template_registry import ...
"""

from __future__ import annotations
import warnings
from typing import List, Optional
from django.core.cache import caches
from django.db.models import Case, When, Value, IntegerField, Q

from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.notifications_template import NotificationTemplate


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



def _locale_chain(locale: str | None) -> List[str]:
    if not locale:
        return ["en"]
    loc = locale.replace("_", "-")
    parts = loc.split("-")
    chain = [loc]
    if len(parts) > 1:
        chain.append(parts[0])
    if "en" not in chain:
        chain.append("en")
    return chain

def _cache_get(key: str):
    try:
        return caches["default"].get(key)
    except Exception:
        return None

def _cache_set(key: str, val, timeout=300):
    try:
        caches["default"].set(key, val, timeout)
    except Exception:
        pass

def resolve_template(
    event: NotificationEvent | str,
    channel: str,
    website_id: Optional[int],
    locale: str = "en",
    use_cache: bool = True,
) -> Optional[NotificationTemplate]:
    """Tenant override > global; exact-locale > lang > en; highest version."""
    if isinstance(event, str):
        ev = NotificationEvent.objects.filter(key=event, enabled=True).only("id", "key").first()
        if not ev:
            return None
        event_id, event_key = ev.id, ev.key
    else:
        event_id, event_key = event.id, event.key

    locales = _locale_chain(locale)
    ck = f"notif:t:{event_key}:{channel}:{website_id or 'global'}:{'/'.join(locales)}"
    if use_cache:
        cached_id = _cache_get(ck)
        if cached_id:
            tpl = NotificationTemplate.objects.filter(pk=cached_id).first()
            if tpl:
                return tpl

    q = NotificationTemplate.objects.filter(
        event_id=event_id, channel=channel, locale__in=locales
    ).filter(Q(website_id=website_id) | Q(website_id__isnull=True))

    website_score = Case(
        When(website_id=website_id, then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    )
    weights = {loc: idx + 1 for idx, loc in enumerate(reversed(locales))}
    whens = [When(locale=l, then=Value(weights[l])) for l in locales]
    locale_score = Case(*whens, default=Value(0), output_field=IntegerField())

    tpl = (
        q.annotate(_w=website_score, _l=locale_score)
         .order_by("-_w", "-_l", "-version", "-id")
         .first()
    )

    if tpl and use_cache:
        _cache_set(ck, tpl.pk, timeout=300)
    return tpl