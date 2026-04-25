from __future__ import annotations

import logging

from celery import shared_task

from orders.models.orders.order import Order
from orders.services.order_approval_service import (
    OrderApprovalService,
)
from orders.services.order_reminder_service import (
    OrderReminderService,
)
from orders.models.orders.enums import OrderStatus

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def auto_approve_eligible_orders(self) -> dict[str, int]:
    """
    Automatically approve orders that have exceeded the approval window.

    Returns:
        dict[str, int]:
            Processing summary containing scanned, approved, and failed
            counts.
    """
    scanned = 0
    approved = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.SUBMITTED,
        approved_at__isnull=True,
    ).only(
        "id",
        "status",
        "submitted_at",
        "approved_at",
        "completed_at",
        "website_id",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            if not OrderApprovalService.can_auto_approve(order=order):
                continue

            OrderApprovalService.auto_approve_order(
                order=order,
                triggered_by=None,
            )
            approved += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to auto approve order.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "approved": approved,
        "failed": failed,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_order_approval_reminders(self) -> dict[str, int]:
    """
    Send approval reminders for submitted orders awaiting client action.

    Returns:
        dict[str, int]:
            Processing summary containing scanned, reminded, and failed
            counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.SUBMITTED,
        approved_at__isnull=True,
    ).select_related(
        "website",
        "client",
    ).only(
        "id",
        "status",
        "submitted_at",
        "approved_at",
        "website_id",
        "client_id",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            was_sent = OrderReminderService.send_approval_reminder(
                order=order,
                triggered_by=None,
            )
            if was_sent:
                reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send approval reminder.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }