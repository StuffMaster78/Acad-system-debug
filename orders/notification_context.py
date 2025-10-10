# orders/notification_context.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from django.conf import settings
from django.urls import reverse, NoReverseMatch


@dataclass(frozen=True)
class Urls:
    """Container for commonly used URLs."""
    order: str = ""
    client_dashboard: str = ""
    writer_dashboard: str = ""
    approve: str = ""
    rate: str = ""
    upload: str = ""


def _safe_str(v: Any) -> str:
    """Return a safe string representation."""
    return "" if v is None else str(v)


def _bool(v: Any) -> bool:
    """Coerce to bool safely."""
    return bool(v)


def _to_float(v: Any) -> Optional[float]:
    """Convert Decimal/int/str to float, else None."""
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except Exception:
        return None


def _iso(dt: Optional[datetime]) -> str:
    """ISO 8601 for datetimes; ensure tz-aware if possible."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _try_reverse(name: str, **kwargs) -> str:
    """Best-effort URL reversing with graceful fallback.

    Args:
        name: URL pattern name.
        **kwargs: Reversal kwargs.

    Returns:
        Absolute or relative URL string or empty string.
    """
    try:
        return reverse(name, kwargs=kwargs)
    except NoReverseMatch:
        return ""


def _time_left(deadline: Optional[datetime]) -> str:
    """Human-friendly time left string (naive)."""
    if not deadline:
        return ""
    now = datetime.now(timezone.utc)
    delta = deadline - now
    secs = int(delta.total_seconds())
    if secs <= 0:
        return "0s"
    mins, s = divmod(secs, 60)
    hrs, m = divmod(mins, 60)
    days, h = divmod(hrs, 24)
    if days:
        return f"{days}d {h}h"
    if hrs:
        return f"{hrs}h {m}m"
    if mins:
        return f"{mins}m"
    return f"{s}s"


def _logo_url(website: Any) -> str:
    """Return a logo URL if your Website model exposes one."""
    url = getattr(website, "logo_url", None)
    if url:
        return url
    return getattr(settings, "DEFAULT_LOGO_URL", "")


def _site_name(website: Any) -> str:
    """Return a human name for the current site/brand."""
    return getattr(website, "name", None) or \
        getattr(settings, "SITE_NAME", "Your Site")


def _site_domain(website: Any) -> str:
    """Return site domain if available."""
    return getattr(website, "domain", "") or ""


def _currency_symbol(code: Optional[str]) -> str:
    """Very small map; extend as needed."""
    m = {"USD": "$", "EUR": "€", "GBP": "£"}
    return m.get((code or "").upper(), "")


def _user_bits(user: Any) -> Dict[str, str]:
    """Minimal safe user info for templates."""
    if not user:
        return {"id": "", "name": "", "email": ""}
    if hasattr(user, "get_full_name"):
        name = user.get_full_name() or getattr(user, "username", "")
    else:
        name = getattr(user, "full_name", None) or \
            getattr(user, "username", "")
    email = getattr(user, "email", "") or ""
    uid = getattr(user, "pk", getattr(user, "id", ""))
    return {"id": _safe_str(uid), "name": _safe_str(name), "email": email}


def _order_urls(order: Any) -> Urls:
    """Compute common deep links for an order."""
    oid = getattr(order, "pk", getattr(order, "id", None))
    oid = _safe_str(oid)
    return Urls(
        order=_try_reverse("orders:detail", pk=oid),
        client_dashboard=_try_reverse("client:orders"),
        writer_dashboard=_try_reverse("writer:orders"),
        approve=_try_reverse("orders:approve", pk=oid),
        rate=_try_reverse("orders:rate", pk=oid),
        upload=_try_reverse("orders:upload", pk=oid),
    )


def _order_bits(order: Any) -> Dict[str, Any]:
    """Extract normalized order fields for templates."""
    if not order:
        return {}
    price = _to_float(getattr(order, "price", None))
    currency = _safe_str(getattr(order, "currency", None))
    deadline = getattr(order, "deadline_at", None)
    status = _safe_str(getattr(order, "status", None))
    num = _safe_str(getattr(order, "number", ""))
    topic = _safe_str(getattr(order, "topic", ""))
    level = _safe_str(getattr(order, "level", ""))
    pages = getattr(order, "pages", None) or 0
    return {
        "id": _safe_str(getattr(order, "pk", getattr(order, "id", ""))),
        "number": num,
        "status": status,
        "topic": topic,
        "level": level,
        "pages": pages,
        "price": price,
        "currency": currency,
        "currency_symbol": _currency_symbol(currency),
        "deadline_at": _iso(deadline),
        "is_overdue": bool(deadline and deadline < datetime.now(timezone.utc)),
        "time_left": _time_left(deadline),
    }


def _cta_defaults(event: str, urls: Urls) -> Dict[str, str]:
    """Suggest a CTA text/url based on event."""
    mapping = {
        "order.created": ("View order", urls.order),
        "order.assigned": ("Start work", urls.order),
        "order.in_progress": ("Open order", urls.order),
        "order.submitted": ("Review files", urls.order),
        "order.revision_requested": ("View revision", urls.order),
        "order.revision_in_progress": ("Continue", urls.order),
        "order.revised": ("Review changes", urls.order),
        "order.approved": ("Rate order", urls.rate),
        "order.paid": ("View receipt", urls.order),
        "order.payment_failed": ("Fix payment", urls.order),
        "order.completed": ("View order", urls.order),
    }
    text, url = mapping.get(event, ("Open", urls.order))
    return {"cta_text": text, "cta_url": url}


def build_order_context(
    *,
    event: str,
    order: Any,
    actor: Optional[Any] = None,
    website: Optional[Any] = None,
    viewer_role: Optional[str] = None,
    subject: Optional[str] = None,
    preheader: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a rich, consistent context dictionary for order templates.

    Args:
        event: Canonical event key (e.g. "order.assigned").
        order: Order domain object.
        actor: User who triggered the event, if any.
        website: Website/tenant object, if any.
        viewer_role: Intended recipient role (e.g. "client").
        subject: Optional subject override for emails.
        preheader: Optional preheader preview for emails.

    Returns:
        dict: Context payload safe for JSON and templates.
    """
    if not order:
        return {
            "event": event,
            "site": {"name": _site_name(website), "logo_url": _logo_url(website),
                     "domain": _site_domain(website)},
            "order": {},
            "client": _user_bits(None),
            "writer": _user_bits(None),
            "actor": _user_bits(actor),
            "urls": {},
            "presentation": {"subject": subject or "", "preheader": preheader or
                             "", "cta_text": "Open", "cta_url": ""},
            "viewer": {"role": viewer_role or ""},
        }

    if website is None:
        website = getattr(order, "website", None)

    urls = _order_urls(order)
    order_d = _order_bits(order)
    client_d = _user_bits(getattr(order, "client", None))
    writer_d = _user_bits(getattr(order, "writer", None))
    actor_d = _user_bits(actor)

    base = {
        "event": event,
        "site": {
            "name": _site_name(website),
            "logo_url": _logo_url(website),
            "domain": _site_domain(website),
        },
        "order": {**order_d, "url": urls.order},
        "client": client_d,
        "writer": writer_d,
        "actor": actor_d,
        "urls": {
            "order": urls.order,
            "client_dashboard": urls.client_dashboard,
            "writer_dashboard": urls.writer_dashboard,
            "approve": urls.approve,
            "rate": urls.rate,
            "upload": urls.upload,
        },
        "presentation": {
            "subject": subject or "",
            "preheader": preheader or "",
            **_cta_defaults(event, urls),
        },
        "viewer": {"role": viewer_role or ""},
    }
    return base