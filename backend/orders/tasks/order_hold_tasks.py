from __future__ import annotations

import logging

from celery import shared_task

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order_hold import OrderHold

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_pending_hold_request_reminders(self) -> dict[str, int]:
    """
    Remind staff about pending hold requests awaiting review.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderHold.objects.filter(
        status="pending",
    ).select_related(
        "website",
        "order",
        "requested_by",
    )

    for hold in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.hold.pending_review_reminder",
                recipient=None,
                website=hold.website,
                context={
                    "hold_id": hold.pk,
                    "order_id": hold.order.pk,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send hold review reminder.",
                extra={"hold_id": hold.pk},
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
def send_stale_active_hold_reminders(self) -> dict[str, int]:
    """
    Remind staff about active holds that may need review or release.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderHold.objects.filter(
        status="active",
    ).select_related(
        "website",
        "order",
        "requested_by",
    )

    for hold in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.hold.active_stale_reminder",
                recipient=None,
                website=hold.website,
                context={
                    "hold_id": hold.pk,
                    "order_id": hold.order.pk,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send stale active hold reminder.",
                extra={"hold_id": hold.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }