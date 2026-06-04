"""
Audit signals for payment and refund events — always sensitive.
"""
from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

log = logging.getLogger("audit")


@receiver(post_save)
def audit_payment_captured(sender, instance, created, **kwargs):
    if sender.__name__ != "PaymentIntent" or not created:
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        client = getattr(instance, "client", None)
        AuditEventFactory.create(
            action="payment.initiated",
            website=getattr(instance, "website", None),
            actor_id=getattr(client, "pk", None) if client else None,
            actor_role=getattr(client, "role", "") if client else "",
            object_type="payment_intent",
            object_id=str(instance.pk),
            metadata={
                "amount": str(getattr(instance, "amount", "")),
                "currency": getattr(instance, "currency", "USD"),
                "payable_type": getattr(instance, "payable_type", ""),
                "provider": getattr(instance, "provider", ""),
            },
            severity="info",
            is_sensitive=True,
            sensitivity_level="payment",
            service_name="payments",
        )
    except Exception:
        log.exception("audit_payment_captured failed")


@receiver(post_save)
def audit_refund(sender, instance, created, **kwargs):
    if sender.__name__ != "Refund" or not created:
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        client = getattr(instance, "client", None)
        order = getattr(instance, "order", None)
        AuditEventFactory.create(
            action="payment.refund_issued",
            website=getattr(instance, "website", None),
            actor_id=getattr(client, "pk", None) if client else None,
            object_type="refund",
            object_id=str(instance.pk),
            metadata={
                "amount": str(getattr(instance, "amount", "")),
                "method": getattr(instance, "method", ""),
                "order_id": getattr(order, "pk", None),
            },
            severity="warning",
            is_sensitive=True,
            sensitivity_level="refund",
            service_name="payments",
        )
    except Exception:
        log.exception("audit_refund failed")


@receiver(post_save)
def audit_wallet_funding(sender, instance, created, **kwargs):
    """Log significant wallet credit events (top-ups, payouts)."""
    if sender.__name__ != "WalletEntry" or not created:
        return
    entry_type = getattr(instance, "entry_type", "")
    # Only log funding and payout events, not routine debits
    if entry_type not in {"funding", "payout", "order_refund"}:
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        created_by = getattr(instance, "created_by", None)
        AuditEventFactory.create(
            action=f"wallet.{entry_type}",
            website=getattr(instance, "website", None),
            actor_id=getattr(created_by, "pk", None) if created_by else None,
            object_type="wallet_entry",
            object_id=str(instance.pk),
            metadata={
                "amount": str(getattr(instance, "amount", "")),
                "direction": getattr(instance, "direction", ""),
                "balance_after": str(getattr(instance, "balance_after", "")),
            },
            severity="info",
            is_sensitive=entry_type == "payout",
            sensitivity_level="payout" if entry_type == "payout" else None,
            service_name="wallets",
        )
    except Exception:
        log.exception("audit_wallet_funding failed")
