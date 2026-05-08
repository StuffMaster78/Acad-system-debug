from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from audit_logging.factories.audit_event_factory import (
    AuditEventFactory,
)


@receiver(post_save, sender=Order)
def audit_order_created(
    sender,
    instance,
    created,
    **kwargs,
):
    if not created:
        return

    AuditEventFactory.create(
        website=instance.website,
        action="order.created",
        actor_id=getattr(instance, "created_by_id", None),
        object_type="order",
        object_id=str(instance.id),
        metadata={
            "status": instance.status,
            "total_amount": str(instance.total_amount),
        },
        severity="info",
    )