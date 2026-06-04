"""
Audit signals for order lifecycle events.
Cancellation, disputes, and resolution are sensitive events.
"""
from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

log = logging.getLogger("audit")


def _website(instance):
    return getattr(instance, "website", None)


def _order_meta(order):
    return {
        "topic": getattr(order, "topic", ""),
        "status": getattr(order, "status", ""),
        "total_price": str(getattr(order, "total_price", "") or ""),
        "client_id": getattr(order, "client_id", None),
    }


def _record_order_transition(order, action: str, extra: dict | None = None,
                              is_sensitive: bool = False, sensitivity_level: str | None = None,
                              severity: str = "info"):
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        meta = _order_meta(order)
        if extra:
            meta.update(extra)
        AuditEventFactory.create(
            action=action,
            website=_website(order),
            object_type="order",
            object_id=str(order.pk),
            metadata=meta,
            severity=severity,
            is_sensitive=is_sensitive,
            sensitivity_level=sensitivity_level,
            service_name="orders",
        )
    except Exception:
        log.exception("order audit signal failed for %s", action)


@receiver(post_save)
def audit_order_status_transitions(sender, instance, created, **kwargs):
    """Watch Order status changes for high-value transitions."""
    if sender.__name__ != "Order" or created:
        return
    status = getattr(instance, "status", "")
    if status == "cancelled":
        _record_order_transition(instance, "order.cancelled",
                                 is_sensitive=True, sensitivity_level="order_cancelled", severity="warning")
    elif status == "completed":
        _record_order_transition(instance, "order.completed")
    elif status == "revision_requested":
        _record_order_transition(instance, "order.revision_requested")
    elif status == "refunded":
        _record_order_transition(instance, "order.refunded",
                                 is_sensitive=True, sensitivity_level="order_refunded", severity="warning")


@receiver(post_save)
def audit_dispute_events(sender, instance, created, **kwargs):
    if sender.__name__ != "OrderDispute":
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        order = getattr(instance, "order", None)
        website = _website(order) if order else None
        actor = getattr(instance, "opened_by", None)
        meta = {
            "reason": getattr(instance, "reason", ""),
            "status": getattr(instance, "status", ""),
            "order_id": getattr(order, "pk", None),
        }
        if created:
            AuditEventFactory.create(
                action="order.disputed",
                website=website,
                actor_id=getattr(actor, "pk", None) if actor else None,
                actor_role=getattr(actor, "role", "") if actor else "",
                actor_display=(actor.get_full_name() or actor.username) if actor else "",
                object_type="order",
                object_id=str(getattr(order, "pk", "")),
                metadata=meta,
                severity="warning",
                is_sensitive=True,
                sensitivity_level="order_disputed",
                service_name="disputes",
            )
        elif getattr(instance, "status", "") in {"resolved", "closed"}:
            AuditEventFactory.create(
                action="order.dispute_resolved",
                website=website,
                object_type="order",
                object_id=str(getattr(order, "pk", "")),
                metadata={**meta, "outcome": getattr(instance, "status", "")},
                severity="info",
                is_sensitive=True,
                sensitivity_level="dispute_resolved",
                service_name="disputes",
            )
    except Exception:
        log.exception("audit_dispute_events failed")


@receiver(post_save)
def audit_assignment(sender, instance, created, **kwargs):
    if sender.__name__ != "OrderAssignment" or not created:
        return
    from audit_logging.factories.audit_event_factory import AuditEventFactory
    try:
        order = getattr(instance, "order", None)
        writer = getattr(instance, "writer", None)
        AuditEventFactory.create(
            action="order.writer_assigned",
            website=_website(order) if order else None,
            object_type="order",
            object_id=str(getattr(order, "pk", "")),
            metadata={
                "writer_id": getattr(writer, "pk", None),
                "source": getattr(instance, "source", ""),
            },
            severity="info",
            service_name="staffing",
        )
    except Exception:
        log.exception("audit_assignment failed")
