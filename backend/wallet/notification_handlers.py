# wallet/notification_handlers.py
from __future__ import annotations

"""Wallet notification handlers.

These handlers register lightweight functions (via the project's
notification handler registry) that forward enriched context to the
notification service. They keep business logic out of the registry and
ensure a consistent payload shape for templates (email/in-app/push).

Each handler:
  * builds a rich context with build_wallet_context(...)
  * shallow-merges any provided payload
  * calls NotificationService.send_notification(...)
"""

from typing import Any, Dict, Optional

from notifications_system.registry.handler_registry import (
    notification_handler,
)
from notifications_system.services.core import NotificationService
from .notification_context import build_wallet_context


def _merge(a: Optional[Dict[str, Any]], b: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow-merge dictionaries with ``b`` overriding.

    Args:
        a: Existing/partial payload.
        b: Context produced for the event.

    Returns:
        A new dictionary containing keys from both mappings.
    """
    base = dict(a or {})
    base.update(b)
    return base


def _send(
    *,
    user: Any,
    event: str,
    payload: Optional[Dict[str, Any]],
    subject: str,
    preheader: str,
    **kwargs: Any,
) -> None:
    """Common sender used by all wallet handlers.

    Args:
        user: Recipient user instance.
        event: Canonical event key (e.g., ``wallet.funded``).
        payload: Optional custom payload to merge.
        subject: Default subject hint for email templates.
        preheader: Optional preheader/preview text.
        **kwargs: Extra args passed by emitters (wallet/actor/website/...).
    """
    ctx = build_wallet_context(
        event=event,
        wallet=kwargs.get("wallet"),
        actor=kwargs.get("actor"),
        website=kwargs.get("website"),
        viewer_role=kwargs.get("viewer_role"),
        subject=subject,
        preheader=preheader,
    )
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=_merge(payload, ctx),
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@notification_handler("wallet.funded")
def on_wallet_funded(*, user, event, payload=None, **kw) -> None:
    """Wallet balance increased by a successful deposit."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Wallet funded",
        preheader="Your deposit was successful.",
        **kw,
    )


@notification_handler("wallet.deposit_pending")
def on_deposit_pending(*, user, event, payload=None, **kw) -> None:
    """A deposit was created and is pending confirmation."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Deposit pending",
        preheader="We are processing your deposit.",
        **kw,
    )


@notification_handler("wallet.deposit_failed")
def on_deposit_failed(*, user, event, payload=None, **kw) -> None:
    """A deposit attempt failed."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Deposit failed",
        preheader="Your deposit attempt did not go through.",
        **kw,
    )


@notification_handler("wallet.withdrawal_requested")
def on_withdrawal_requested(*, user, event, payload=None, **kw) -> None:
    """A withdrawal request was created by the user."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Withdrawal requested",
        preheader="Your withdrawal request is being reviewed.",
        **kw,
    )


@notification_handler("wallet.withdrawal_approved")
def on_withdrawal_approved(*, user, event, payload=None, **kw) -> None:
    """A withdrawal request was approved by staff."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Withdrawal approved",
        preheader="Your withdrawal was approved.",
        **kw,
    )


@notification_handler("wallet.withdrawal_paid")
def on_withdrawal_paid(*, user, event, payload=None, **kw) -> None:
    """Funds have been paid out for a withdrawal."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Withdrawal paid",
        preheader="Your withdrawal has been paid out.",
        **kw,
    )


@notification_handler("wallet.withdrawal_rejected")
def on_withdrawal_rejected(*, user, event, payload=None, **kw) -> None:
    """A withdrawal request was rejected."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Withdrawal rejected",
        preheader="Your withdrawal request was not approved.",
        **kw,
    )


@notification_handler("wallet.transfer_sent")
def on_transfer_sent(*, user, event, payload=None, **kw) -> None:
    """User sent a transfer from their wallet."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Transfer sent",
        preheader="Your wallet transfer has been sent.",
        **kw,
    )


@notification_handler("wallet.transfer_received")
def on_transfer_received(*, user, event, payload=None, **kw) -> None:
    """User received a wallet transfer."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Transfer received",
        preheader="You have received a wallet transfer.",
        **kw,
    )


@notification_handler("wallet.refund_issued")
def on_refund_issued(*, user, event, payload=None, **kw) -> None:
    """A refund was credited back to the wallet."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Refund issued",
        preheader="A refund has been credited to your wallet.",
        **kw,
    )


@notification_handler("wallet.balance_low")
def on_balance_low(*, user, event, payload=None, **kw) -> None:
    """Balance dropped below the low threshold."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Low wallet balance",
        preheader="Your wallet balance is getting low.",
        **kw,
    )


@notification_handler("wallet.balance_critical")
def on_balance_critical(*, user, event, payload=None, **kw) -> None:
    """Balance reached a critical threshold."""
    _send(
        user=user,
        event=event,
        payload=payload,
        subject="Critical wallet balance",
        preheader="Your wallet balance is critical.",
        **kw,
    )
