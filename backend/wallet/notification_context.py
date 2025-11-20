from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from django.conf import settings
from django.urls import NoReverseMatch, reverse


@dataclass(frozen=True)
class Urls:
    """Common wallet URLs used by templates."""
    wallet: str = ""
    transactions: str = ""
    deposit: str = ""
    withdraw: str = ""
    settings: str = ""


def _safe_str(v: Any) -> str:
    """Return a safe string representation."""
    return "" if v is None else str(v)


def _try_reverse(name: str, **kwargs: Any) -> str:
    """Best-effort reverse with graceful fallback.

    Args:
        name: URL pattern name.
        **kwargs: kwargs passed to ``reverse``.

    Returns:
        URL string or empty string if reversing fails.
    """
    try:
        return reverse(name, kwargs=kwargs)
    except NoReverseMatch:
        return ""


def _logo_url(website: Any) -> str:
    """Return a logo URL if Website exposes one or use a default."""
    url = getattr(website, "logo_url", None)
    if url:
        return url
    return getattr(settings, "DEFAULT_LOGO_URL", "")


def _site_name(website: Any) -> str:
    """Return a human name for the current site/brand."""
    return (
        getattr(website, "name", None)
        or getattr(settings, "SITE_NAME", "Your Site")
    )


def _user_bits(user: Any) -> Dict[str, str]:
    """Minimal safe user info for templates.

    Returns:
        Dict with ``id``, ``name``, and ``email`` keys.
    """
    if not user:
        return {"id": "", "name": "", "email": ""}
    name = (
        user.get_full_name()  # type: ignore[attr-defined]
        if hasattr(user, "get_full_name")
        else getattr(user, "full_name", None) or getattr(user, "username", "")
    )
    email = getattr(user, "email", "") or ""
    uid = getattr(user, "pk", getattr(user, "id", ""))
    return {"id": _safe_str(uid), "name": _safe_str(name), "email": email}


def _wallet_urls(wallet: Any) -> Urls:
    """Compute common deep links for a wallet.

    Expects your project to define these named URLs (optional):
      - wallet:detail (pk)
      - wallet:transactions (pk)
      - wallet:deposit (pk)
      - wallet:withdraw (pk)
      - wallet:settings (pk)
    """
    wid = getattr(wallet, "pk", getattr(wallet, "id", None))
    wid = _safe_str(wid)
    return Urls(
        wallet=_try_reverse("wallet:detail", pk=wid),
        transactions=_try_reverse("wallet:transactions", pk=wid),
        deposit=_try_reverse("wallet:deposit", pk=wid),
        withdraw=_try_reverse("wallet:withdraw", pk=wid),
        settings=_try_reverse("wallet:settings", pk=wid),
    )


def _wallet_bits(wallet: Any) -> Dict[str, Any]:
    """Extract normalized wallet fields for templates.

    Returns:
        Dict with safe, serializable wallet fields.
    """
    if not wallet:
        return {}
    currency = getattr(wallet, "currency", None)
    owner = getattr(wallet, "owner", None)
    low = getattr(wallet, "low_threshold", None)
    crit = getattr(wallet, "critical_threshold", None)
    updated = getattr(wallet, "updated_at", None)
    balance = getattr(wallet, "balance", None)

    return {
        "id": _safe_str(getattr(wallet, "pk", getattr(wallet, "id", ""))),
        "number": _safe_str(getattr(wallet, "number", "")),
        "currency": _safe_str(currency),
        "balance": float(balance) if balance is not None else None,
        "low_threshold": float(low) if low is not None else None,
        "critical_threshold": float(crit) if crit is not None else None,
        "updated_at": updated.isoformat() if updated else "",
        "owner": _user_bits(owner),
    }


def _cta_defaults(event: str, urls: Urls) -> Dict[str, str]:
    """Suggest a default CTA based on the wallet event."""
    mapping = {
        "wallet.funded": ("View transactions", urls.transactions),
        "wallet.deposit_pending": ("View deposit", urls.transactions),
        "wallet.deposit_failed": ("Try again", urls.deposit),
        "wallet.withdrawal_requested": ("View withdrawal", urls.transactions),
        "wallet.withdrawal_approved": ("View payout", urls.transactions),
        "wallet.withdrawal_paid": ("View payout", urls.transactions),
        "wallet.withdrawal_rejected": ("Contact support", urls.settings),
        "wallet.transfer_sent": ("View transfer", urls.transactions),
        "wallet.transfer_received": ("View credit", urls.transactions),
        "wallet.refund_issued": ("View refund", urls.transactions),
        "wallet.balance_low": ("Deposit funds", urls.deposit),
        "wallet.balance_critical": ("Deposit now", urls.deposit),
    }
    text, url = mapping.get(event, ("Open wallet", urls.wallet))
    return {"cta_text": text, "cta_url": url}


def build_wallet_context(
    *,
    event: str,
    wallet: Any,
    actor: Optional[Any] = None,
    website: Optional[Any] = None,
    viewer_role: Optional[str] = None,
    subject: Optional[str] = None,
    preheader: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a rich, consistent context for wallet notifications.

    Args:
        event: Canonical event key (e.g., ``wallet.funded``).
        wallet: Wallet domain object.
        actor: User who triggered the event, if any.
        website: Website/tenant object, if any.
        viewer_role: Intended recipient role (e.g., ``client``).
        subject: Optional subject override for emails.
        preheader: Optional email preheader/preview text.

    Returns:
        A dictionary ready to merge into notification payloads.
    """
    urls = _wallet_urls(wallet)
    wallet_d = _wallet_bits(wallet)
    actor_d = _user_bits(actor)

    base = {
        "event": event,
        "site": {
            "name": _site_name(website),
            "logo_url": _logo_url(website),
        },
        "wallet": wallet_d,
        "actor": actor_d,
        "urls": {
            "wallet": urls.wallet,
            "transactions": urls.transactions,
            "deposit": urls.deposit,
            "withdraw": urls.withdraw,
            "settings": urls.settings,
        },
        "presentation": {
            "subject": subject or "",
            "preheader": preheader or "",
            **_cta_defaults(event, urls),
        },
        "viewer": {"role": viewer_role or ""},
        "meta": {
            "now": datetime.now(timezone.utc).isoformat(),
        },
    }
    return base
