# wallet/notification_templates.py
from __future__ import annotations

"""Class-based wallet templates bound to canonical event keys.

These read the enriched context built by wallet emitters:
  - context["wallet"], ["transaction"], ["payment_method"], ["urls"]
  - context["presentation"].subject/preheader/cta_text/cta_url
Return (title, text, html) from render(context).
"""

from typing import Dict, Tuple

from notifications_system.registry.template_registry import (
    register_template,
    BaseNotificationTemplate,
)


def _title(ctx: Dict, default: str) -> str:
    pres = ctx.get("presentation", {})
    return pres.get("subject") or default


def _pre(ctx: Dict, default: str) -> str:
    pres = ctx.get("presentation", {})
    return pres.get("preheader") or default


def _cta(ctx: Dict) -> Tuple[str, str]:
    pres = ctx.get("presentation", {})
    return pres.get("cta_text", "Open"), pres.get("cta_url", "")


def _html(title: str, body: str, cta_text: str, cta_url: str) -> str:
    cta = f'<p><a href="{cta_url}">{cta_text}</a></p>' if cta_url else ""
    return f"<h3>{title}</h3><p>{body}</p>{cta}"


def _amt(ctx: Dict) -> str:
    txn = ctx.get("transaction", {}) or {}
    val = txn.get("amount")
    cur = txn.get("currency") or ""
    return f" {val} {cur}".strip() if val is not None else ""


def _bal(ctx: Dict) -> str:
    w = ctx.get("wallet", {}) or {}
    val = w.get("balance")
    cur = w.get("currency") or ""
    return f"{val} {cur}".strip() if val is not None else ""


@register_template("wallet.balance_low")
class WalletLowBalance(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Low wallet balance")
        body = _pre(
            ctx, f"Your balance is low ({_bal(ctx)}). Consider topping up."
        )
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.credit_added")
class WalletCreditAdded(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Wallet credited")
        body = _pre(ctx, f"A credit of{_amt(ctx)} was added to your wallet.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.debit_made")
class WalletDebitMade(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Wallet charge")
        body = _pre(ctx, f"A debit of{_amt(ctx)} was charged from wallet.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.topup_failed")
class WalletTopupFailed(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Top-up failed")
        body = _pre(ctx, "Your wallet top-up attempt failed.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.payment_method_expiring")
class WalletPMExpiring(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        pm = ctx.get("payment_method") or {}
        brand = pm.get("brand") or "Payment method"
        last4 = pm.get("last4") or ""
        tail = f" ****{last4}" if last4 else ""
        title = _title(ctx, "Payment method expiring")
        body = _pre(ctx, f"{brand}{tail} is expiring soon.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.withdrawal_requested")
class WalletWithdrawalRequested(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Withdrawal requested")
        body = _pre(ctx, f"You requested a withdrawal of{_amt(ctx)}.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)


@register_template("wallet.withdrawal_processed")
class WalletWithdrawalProcessed(BaseNotificationTemplate):
    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Withdrawal processed")
        body = _pre(ctx, f"Your withdrawal of{_amt(ctx)} was processed.")
        t, u = _cta(ctx)
        return title, body, _html(title, body, t, u)