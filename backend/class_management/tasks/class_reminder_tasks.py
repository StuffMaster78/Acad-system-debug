from __future__ import annotations

from django.utils import timezone

from class_management.selectors.class_payment_selectors import (
    ClassPaymentSelector,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


def send_payment_reminders():
    """
    Notify clients about upcoming or overdue payments.
    """
    installments = ClassPaymentSelector.overdue_installments(
        website=None,
    )

    for inst in installments:
        class_order = inst.plan.class_order

        NotificationService.notify(
            event_key="class.payment.overdue",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.id,
                "amount_due": str(inst.amount),
                "due_at": inst.due_at,
            },
        )