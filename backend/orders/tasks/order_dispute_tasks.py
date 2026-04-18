from __future__ import annotations

import logging

from celery import shared_task

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.disputes.order_dispute import OrderDispute

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_open_dispute_reminders(self) -> dict[str, int]:
    """
    Remind staff about open disputes requiring attention.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderDispute.objects.filter(
        status="open",
    ).select_related(
        "website",
        "order",
        "opened_by",
    )

    for dispute in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.dispute.open_reminder",
                recipient=None,
                website=dispute.website,
                context={
                    "dispute_id": dispute.pk,
                    "order_id": dispute.order.pk,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send open dispute reminder.",
                extra={"dispute_id": dispute.pk},
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
def send_escalated_dispute_reminders(self) -> dict[str, int]:
    """
    Remind staff about escalated disputes that still need resolution.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderDispute.objects.filter(
        status="escalated",
    ).select_related(
        "website",
        "order",
        "opened_by",
    )

    for dispute in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.dispute.escalated_reminder",
                recipient=None,
                website=dispute.website,
                context={
                    "dispute_id": dispute.pk,
                    "order_id": dispute.order.pk,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send escalated dispute reminder.",
                extra={"dispute_id": dispute.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }