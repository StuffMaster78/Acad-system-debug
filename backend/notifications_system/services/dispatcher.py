# notifications_system/services/dispatcher.py
from __future__ import annotations
from django.db import transaction
from django.utils import timezone
from typing import Iterable, List, Optional, Tuple
from django.conf import settings
from django.core.cache import caches
from django.db.models import Case, When, Value, IntegerField, Q
from notifications_system.models.notifications_template import NotificationTemplate
from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.notification_preferences import UserNotificationPreference
from notifications_system.models.delivery import Delivery

from notifications_system.services.render import render_template

def _respect_quiet_hours(pref: Optional[UserNotificationPreference]) -> bool:
    # Implement TZ-aware check if you store it; allow for now.
    return True

def resolve_template(event: NotificationEvent, channel: str,
                     website_id: Optional[int], locale: str = "en"
                     ) -> Optional[NotificationTemplate]:
    qs = NotificationTemplate.objects.filter(
        event=event, channel=channel, locale=locale
    )
    if website_id:
        t = qs.filter(website_id=website_id).order_by("-version").first()
        if t:
            return t
    return qs.filter(website_id__isnull=True).order_by("-version").first()

def should_send(user_id: Optional[int], website_id: Optional[int], channel: str) -> bool:
    if not user_id:
        return True
    pref = UserNotificationPreference.objects.filter(
        user_id=user_id, website_id=website_id, channel=channel
    ).first()
    if pref and not pref.enabled:
        return False
    return _respect_quiet_hours(pref)

def queue_delivery(
    *,
    event_key: str,
    website_id: Optional[int],
    user_id: Optional[int],
    payload: dict,
    channels: list[str],
    priority: str,
    dedupe_key: str = "",
    locale: str = "en",
) -> list[Delivery]:
    event = NotificationEvent.objects.filter(key=event_key, enabled=True).first()
    if not event:
        return []

    deliveries: list[Delivery] = []
    with transaction.atomic():
        for ch in channels:
            if not should_send(user_id, website_id, ch):
                continue
            tmpl = resolve_template(event, ch, website_id, locale)
            if not tmpl:
                continue
            rendered = render_template(tmpl, payload)
            d = Delivery.objects.create(
                event_key=event.key,
                website_id=website_id,
                user_id=user_id,
                channel=ch,
                priority=priority or event.priority,
                payload=payload or {},
                rendered=rendered,
                dedupe_key=dedupe_key,
                status="queued",
                queued_at=timezone.now(),
            )
            deliveries.append(d)
    return deliveries


def _locale_chain(locale: str | None) -> List[str]:
    """Return best-to-worst locale candidates (exact → lang → 'en')."""
    if not locale:
        return ["en"]
    loc = locale.replace("_", "-")
    parts = loc.split("-")
    chain = [loc]
    if len(parts) > 1:
        chain.append(parts[0])  # language-only
    if "en" not in chain:
        chain.append("en")
    return chain


def _cache_get(key: str):
    try:
        cache = caches["default"]
        return cache.get(key)
    except Exception:
        return None


def _cache_set(key: str, value, timeout: int = 300):
    try:
        cache = caches["default"]
        cache.set(key, value, timeout=timeout)
    except Exception:
        pass


def resolve_template(
    event: NotificationEvent | str,
    channel: str,
    website_id: Optional[int],
    locale: str = "en",
    use_cache: bool = True,
) -> Optional[NotificationTemplate]:
    """Pick the best template with tenant + locale fallbacks and highest version.

    Selection order (highest wins):
      1) website-specific over global
      2) exact locale > language-only > 'en'
      3) highest version

    Args:
        event: NotificationEvent instance or event key (str).
        channel: Channel name (e.g., 'email', 'in_app').
        website_id: Tenant/website id or None for global.
        locale: Desired BCP-47-ish locale (e.g., 'sw-KE', 'en').
        use_cache: Use Django cache if available.

    Returns:
        NotificationTemplate or None if not found.
    """
    # Normalize inputs
    if isinstance(event, str):
        ev = NotificationEvent.objects.filter(key=event, enabled=True).only("id").first()
        if not ev:
            return None
        event_id = ev.id
        event_key = event
    else:
        event_id = event.id
        event_key = event.key

    locales = _locale_chain(locale)

    # Cache key (stable, small)
    ck = f"notif:t:{event_key}:{channel}:{website_id or 'global'}:{'/'.join(locales)}"
    if use_cache:
        cached_id = _cache_get(ck)
        if cached_id:
            # Re-fetch by PK to return a live model instance
            tpl = NotificationTemplate.objects.filter(pk=cached_id).first()
            if tpl:
                return tpl

    # Build query with both website and global templates
    q = NotificationTemplate.objects.filter(
        event_id=event_id,
        channel=channel,
        locale__in=locales,
    ).filter(
        Q(website_id=website_id) | Q(website_id__isnull=True)
    )

    # Ranking:
    # website_score: 1 for exact tenant, 0 for global
    website_score = Case(
        When(website_id=website_id, then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    )

    # locale_score: N for exact locale (highest), then language-only, then 'en'
    # give descending weights based on position in locales list
    # e.g., locales = ['sw-KE','sw','en'] → {'sw-KE':3,'sw':2,'en':1}
    weights = {loc: idx + 1 for idx, loc in enumerate(reversed(locales))}
    whens = [When(locale=l, then=Value(weights[l])) for l in locales]
    locale_score = Case(*whens, default=Value(0), output_field=IntegerField())

    # Order: website match desc, locale score desc, version desc, PK desc
    tpl = (
        q.annotate(_wscore=website_score, _lscore=locale_score)
         .order_by("-_wscore", "-_lscore", "-version", "-id")
         .first()
    )

    if tpl and use_cache:
        _cache_set(ck, tpl.pk, timeout=300)

    return tpl