from __future__ import annotations

import logging

from celery import shared_task

from orders.models.orders.order import Order
from orders.services.order_archival_service import (
    OrderArchivalService,
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
def auto_archive_eligible_orders(self) -> dict[str, int]:
    """
    Automatically archive completed orders that have exceeded the
    archival retention window.

    Returns:
        dict[str, int]:
            Processing summary containing scanned, archived, and failed
            counts.
    """
    scanned = 0
    archived = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.COMPLETED,
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