from __future__ import annotations

import logging

from celery import shared_task

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order_reassignment_request import (
    OrderReassignmentRequest,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_pending_reassignment_reminders(self) -> dict[str, int]:
    """
    Remind staff about pending reassignment requests.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderReassignmentRequest.objects.filter(
        status="pending",
    ).select_related(
        "website",
        "order",
        "requested_by",
    )

    for reassignment_request in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.reassignment.pending_reminder",
                recipient=None,
                website=reassignment_request.website,
                context={
                    "reassignment_request_id": reassignment_request.pk,
                    "order_id": reassignment_request.order.pk,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send reassignment reminder.",
                extra={
                    "reassignment_request_id": reassignment_request.pk,
                },
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }