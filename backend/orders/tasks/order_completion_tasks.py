from __future__ import annotations

import logging

from celery import shared_task

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models import Order
from orders.services.order_approval_service import (
    OrderApprovalService,
)
from orders.services.order_archival_service import (
    OrderArchivalService,
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
    Automatically approve submitted orders that crossed the approval window.

    Returns:
        dict[str, int]:
            Summary containing scanned, approved, and failed counts.
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
                "Failed to auto approve eligible order.",
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
def send_completion_approval_reminders(self) -> dict[str, int]:
    """
    Remind clients to approve submitted orders.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
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
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            was_sent = OrderReminderService.send_approval_reminder(
                order=order,
                triggered_by=None,
            )
            if was_sent:
                client = getattr(order, "client", None)
                if client is None:
                        continue

                submitted_at = getattr(order, "submitted_at", None)
                submitted_at_iso = (
                    submitted_at.isoformat()
                    if submitted_at is not None
                    else None
                )
                NotificationService.notify(
                    event_key="order.completion.approval_reminder",
                    recipient=client,
                    website=order.website,
                    context={
                        "order_id": order.pk,
                        "submitted_at": submitted_at_iso,
                    },
                triggered_by=None,
            )
                reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send completion approval reminder.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def auto_archive_eligible_orders(self) -> dict[str, int]:
    """
    Automatically archive completed orders that crossed the retention window.

    Returns:
        dict[str, int]:
            Summary containing scanned, archived, and failed counts.
    """
    scanned = 0
    archived = 0
    failed = 0

    queryset = Order.objects.filter(
        status="completed",
        archived_at__isnull=True,
    ).only(
        "id",
        "status",
        "completed_at",
        "archived_at",
        "website_id",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            if not OrderArchivalService.can_auto_archive(order=order):
                continue

            OrderArchivalService.auto_archive_order(
                order=order,
                triggered_by=None,
            )
            archived += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to auto archive order.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "archived": archived,
        "failed": failed,
    }