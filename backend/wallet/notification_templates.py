# wallet/notification_templates.py
from __future__ import annotations

"""Class-based wallet templates bound to canonical event keys.

Each template reads from enriched context (if provided) with keys like:
  - presentation.subject / preheader / cta_text / cta_url
  - wallet.balance / wallet.currency / wallet.threshold
  - transaction.amount / transaction.currency
  - payment_method.brand / last4 / exp_month / exp_year
  - urls.top_up / urls.history

Return (title, text, html) from ``render``.
"""

from typing import Dict, Tuple

from notifications_system.registry.template_registry import (
    register_template,
    register_template_name,
    BaseNotificationTemplate,
)


def _title(ctx: Dict, default: str) -> str:
    """Return a subject from context or a default."""
    pres = ctx.get("presentation", {})
    return pres.get("subject") or default


def _preheader(ctx: Dict, default: str) -> str:
    """Return preheader/preview text from context or a default."""
    pres = ctx.get("presentation", {})
    return pres.get("preheader") or default


def _cta(ctx: Dict) -> Tuple[str, str]:
    """Return (cta_text, cta_url) with safe defaults."""
    pres = ctx.get("presentation", {})
    return pres.get("cta_text", "Open"), pres.get("cta_url", "")


def _html(title: str, body: str, cta_text: str, cta_url: str) -> str:
    """Very small HTML stub suitable for email/push fallbacks."""
    cta = f'<p><a href="{cta_url}">{cta_text}</a></p>' if cta_url else ""
    return f"<h3>{title}</h3><p>{body}</p>{cta}"


@register_template("wallet.balance_low")
class WalletBalanceLowTpl(BaseNotificationTemplate):
    """Template: client balance dropped below threshold."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        bal = (ctx.get("wallet") or {}).get("balance")
        cur = (ctx.get("wallet") or {}).get("currency", "")
        thr = (ctx.get("wallet") or {}).get("threshold")
        title = _title(ctx, "Balance low")
        pref = _preheader(ctx, "Your wallet balance is low.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Balance: {bal} {cur}; threshold: {thr}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("wallet.credit_added")
class WalletCreditAddedTpl(BaseNotificationTemplate):
    """Template: funds added to wallet."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        amt = (ctx.get("transaction") or {}).get("amount")
        cur = (ctx.get("transaction") or {}).get("currency", "")
        title = _title(ctx, "Credit added")
        pref = _preheader(ctx, "Funds were added to your wallet.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Amount: {amt} {cur}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("wallet.debit_made")
class WalletDebitMadeTpl(BaseNotificationTemplate):
    """Template: charge made against wallet balance."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        amt = (ctx.get("transaction") or {}).get("amount")
        cur = (ctx.get("transaction") or {}).get("currency", "")
        title = _title(ctx, "Debit made")
        pref = _preheader(ctx, "A charge was made from your wallet.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Amount: {amt} {cur}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("wallet.topup_failed")
class WalletTopupFailedTpl(BaseNotificationTemplate):
    """Template: top-up attempt failed."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Top-up failed")
        pref = _preheader(ctx, "Your wallet top-up attempt failed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Please try again or use another method."
        return title, body, _html(title, body, cta_text, cta_url)


# @register_template("wallet.payment_method_expiring")
# class WalletPmExpiringTpl(BaseNotificationTemplate):
#     """Template: saved payment method expiring soon."""

#     def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
#         ctx = {**self.context, **(context or {})}
#         pm = ctx.get("payment_method") or {}
#         brand = pm.get("brand", "")
#         last4 = pm.get("last4", "")
#         exp_m = pm.get("exp_month", "")
#         exp_y = pm.get("exp_year", "")
#         title = _title(ctx, "Payment method expiring")
#         pref = _preheader(ctx, "Update your payment method to avoid issues.")
#         cta_text, cta_url = _cta(ctx)
#         body = (
#             f"{pref} {brand} •••• {last4} expires {exp_m}/{exp_y}."
#         )
#         return title, body, _html(title, body, cta_text, cta_url)


@register_template("wallet.withdrawal_requested")
class WalletWithdrawalRequestedTpl(BaseNotificationTemplate):
    """Template: client requested a withdrawal."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        amt = (ctx.get("transaction") or {}).get("amount")
        cur = (ctx.get("transaction") or {}).get("currency", "")
        title = _title(ctx, "Withdrawal requested")
        pref = _preheader(ctx, "We received your withdrawal request.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Amount: {amt} {cur}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("wallet.withdrawal_processed")
class WalletWithdrawalProcessedTpl(BaseNotificationTemplate):
    """Template: withdrawal has been processed/payout sent."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        amt = (ctx.get("transaction") or {}).get("amount")
        cur = (ctx.get("transaction") or {}).get("currency", "")
        title = _title(ctx, "Withdrawal processed")
        pref = _preheader(ctx, "Your withdrawal has been processed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Amount: {amt} {cur}."
        return title, body, _html(title, body, cta_text, cta_url)


# Optional: if you keep file-based email templates too, map them here.
register_template_name(
    event_key="wallet.balance_low",
    channel="email",
    template_name="notifications/emails/wallet_balance_low.html",
)