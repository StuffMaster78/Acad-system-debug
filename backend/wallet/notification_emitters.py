# wallet/notification_emitters.py
from __future__ import annotations

"""Emit wallet events with a consistent, enriched context.

This module provides a small, public API for emitting wallet events
into the notifications pipeline. It builds a serializable context and
dispatches to the project's handler registry.

Usage:
    from wallet.notification_emitters import emit_wallet_credit_added
    emit_wallet_credit_added(wallet=wallet, transaction=txn, actor=user)

Event keys emitted here:
    - wallet.balance_low
    - wallet.credit_added
    - wallet.debit_made
    - wallet.topup_failed
    - wallet.payment_method_expiring
    - wallet.withdrawal_requested
    - wallet.withdrawal_processed
"""

from typing import Any, Mapping, Optional, Dict

from django.utils import timezone
from django.urls import reverse, NoReverseMatch

from notifications_system.registry.handler_registry import dispatch

# If you later add a richer builder under wallet.notification_context,
# you can import it here and prefer it over _default_ctx (as in orders).


def _try_reverse(name: str, **kwargs: Any) -> str:
    """Best-effort reverse with graceful fallback.

    Args:
        name: URL pattern name.
        **kwargs: Reverse kwargs.

    Returns:
        A URL string or empty string if no matching route exists.
    """
    try:
        return reverse(name, kwargs=kwargs)
    except NoReverseMatch:
        return ""


def _payment_method_bits(pm: Any) -> Dict[str, Any]:
    """Normalize minimal payment method fields.

    Args:
        pm: Payment method-like object.

    Returns:
        Mapping with brand/last4/expiry or empty values.
    """
    if not pm:
        return {"brand": "", "last4": "", "exp_month": "", "exp_year": ""}
    return {
        "brand": getattr(pm, "brand", "") or "",
        "last4": getattr(pm, "last4", "") or "",
        "exp_month": getattr(pm, "exp_month", "") or "",
        "exp_year": getattr(pm, "exp_year", "") or "",
    }


def _transaction_bits(txn: Any) -> Dict[str, Any]:
    """Normalize minimal transaction fields.

    Args:
        txn: Transaction-like object.

    Returns:
        Mapping with amount/currency/id/status.
    """
    if not txn:
        return {"id": None, "amount": None, "currency": "", "status": ""}
    return {
        "id": getattr(txn, "id", None),
        "amount": getattr(txn, "amount", None),
        "currency": getattr(txn, "currency", "") or "",
        "status": getattr(txn, "status", "") or "",
    }


def _user_bits(user: Any) -> Dict[str, Any]:
    """Normalize minimal user fields.

    Args:
        user: User-like object.

    Returns:
        Mapping with id, email and display name.
    """
    if not user:
        return {"id": None, "email": "", "name": ""}
    name = ""
    if hasattr(user, "get_full_name"):
        try:
            name = user.get_full_name() or ""
        except Exception:  # pragma: no cover
            name = ""
    if not name:
        name = getattr(user, "full_name", None) or getattr(
            user, "username", ""
        )
    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", "") or "",
        "name": name,
    }


def _wallet_bits(wallet: Any) -> Dict[str, Any]:
    """Normalize minimal wallet fields.

    Args:
        wallet: Wallet-like object.

    Returns:
        Mapping with id, balance, currency, threshold.
    """
    if not wallet:
        return {
            "id": None,
            "balance": None,
            "currency": "",
            "threshold": None,
        }
    return {
        "id": getattr(wallet, "id", None),
        "balance": getattr(wallet, "balance", None),
        "currency": getattr(wallet, "currency", "") or "",
        "threshold": getattr(wallet, "low_balance_threshold", None),
    }


def _urls(wallet: Any) -> Dict[str, str]:
    """Common deep-links for wallet UX.

    Args:
        wallet: Wallet-like object.

    Returns:
        Mapping of useful URLs (may be empty strings).
    """
    wid = getattr(wallet, "id", None)
    return {
        "top_up": _try_reverse("wallet:top_up", pk=wid),
        "history": _try_reverse("wallet:history", pk=wid),
        "settings": _try_reverse("wallet:settings"),
    }


def _default_ctx(
    *,
    event: str,
    wallet: Any,
    actor: Optional[Any] = None,
    transaction: Optional[Any] = None,
    payment_method: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a minimal, serializable context for wallet events.

    Args:
        event: Canonical event key (e.g., 'wallet.credit_added').
        wallet: Wallet-like object.
        actor: Optional user who triggered the event.
        transaction: Optional transaction-like object.
        payment_method: Optional payment method-like object.
        extra: Optional mapping merged shallowly.

    Returns:
        Dict ready to serialize and pass to templates.
    """
    owner = getattr(wallet, "owner", None) if wallet else None
    ctx: Dict[str, Any] = {
        "event": event,
        "now": timezone.now().isoformat(),
        "wallet": _wallet_bits(wallet),
        "owner": _user_bits(owner),
        "actor": _user_bits(actor),
        "transaction": _transaction_bits(transaction),
        "payment_method": _payment_method_bits(payment_method),
        "urls": _urls(wallet),
        "presentation": {
            # Templates may override these; placeholders here.
            "subject": "",
            "preheader": "",
            "cta_text": "Open",
            "cta_url": _urls(wallet).get("history", ""),
        },
    }
    if extra:
        ctx.update(dict(extra))
    return ctx


def emit_event(
    event_key: str,
    *,
    wallet: Any,
    actor: Optional[Any] = None,
    transaction: Optional[Any] = None,
    payment_method: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Emit a wallet event to the handler registry.

    Args:
        event_key: Canonical key (e.g., 'wallet.balance_low').
        wallet: Wallet-like object.
        actor: Optional user who triggered the event.
        transaction: Optional transaction-like object.
        payment_method: Optional payment method-like object.
        extra: Optional extra context to merge.

    Returns:
        None.
    """
    ctx = _default_ctx(
        event=event_key,
        wallet=wallet,
        actor=actor,
        transaction=transaction,
        payment_method=payment_method,
        extra=extra,
    )
    dispatch(event_key, ctx)


# -- Convenience emitters ----------------------------------------------------


def emit_wallet_balance_low(
    *,
    wallet: Any,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Balance fell below threshold."""
    emit_event("wallet.balance_low", wallet=wallet, actor=actor, extra=extra)


def emit_wallet_credit_added(
    *,
    wallet: Any,
    transaction: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Funds added to wallet."""
    emit_event(
        "wallet.credit_added",
        wallet=wallet,
        transaction=transaction,
        actor=actor,
        extra=extra,
    )


def emit_wallet_debit_made(
    *,
    wallet: Any,
    transaction: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Charge made against wallet."""
    emit_event(
        "wallet.debit_made",
        wallet=wallet,
        transaction=transaction,
        actor=actor,
        extra=extra,
    )


def emit_wallet_topup_failed(
    *,
    wallet: Any,
    transaction: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Top-up attempt failed."""
    emit_event(
        "wallet.topup_failed",
        wallet=wallet,
        transaction=transaction,
        actor=actor,
        extra=extra,
    )


def emit_wallet_payment_method_expiring(
    *,
    wallet: Any,
    payment_method: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Saved payment method is expiring soon."""
    emit_event(
        "wallet.payment_method_expiring",
        wallet=wallet,
        payment_method=payment_method,
        actor=actor,
        extra=extra,
    )


def emit_wallet_withdrawal_requested(
    *,
    wallet: Any,
    transaction: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Client requested a withdrawal."""
    emit_event(
        "wallet.withdrawal_requested",
        wallet=wallet,
        transaction=transaction,
        actor=actor,
        extra=extra,
    )


def emit_wallet_withdrawal_processed(
    *,
    wallet: Any,
    transaction: Optional[Any] = None,
    actor: Optional[Any] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> None:
    """Withdrawal processed / payout sent."""
    emit_event(
        "wallet.withdrawal_processed",
        wallet=wallet,
        transaction=transaction,
        actor=actor,
        extra=extra,
    )