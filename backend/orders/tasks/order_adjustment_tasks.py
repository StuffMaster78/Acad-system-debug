from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models import OrderAdjustmentFunding, OrderAdjustmentRequest

logger = logging.getLogger(__name__)


class OrderAdjustmentTaskConfig:
    """
    Hold operational configuration for adjustment task flows.
    """

    RESPONSE_WINDOW_DAYS = 7


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_pending_adjustment_response_reminders(
    self,
) -> dict[str, int]:
    """
    Remind clients about adjustment requests awaiting response.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderAdjustmentRequest.objects.filter(
        status="pending_client_response",
    ).select_related(
        "website",
        "order",
    )

    for adjustment_request in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            order = adjustment_request.order
            client = getattr(order, "client", None)
            if client is None:
                continue

            NotificationService.notify(
                event_key="order.adjustment.pending_client_response_reminder",
                recipient=client,
                website=adjustment_request.website,
                context={
                    "adjustment_request_id": adjustment_request.pk,
                    "order_id": order.pk,
                },
                triggered_by=None,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send adjustment response reminder.",
                extra={"adjustment_request_id": adjustment_request.pk},
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
def expire_stale_adjustments(self) -> dict[str, int]:
    """
    Expire stale adjustment requests after the response window.

    Notes:
        This uses created_at as the first pass rule.
        If you later add expires_at, switch this task to use it.

    Returns:
        dict[str, int]:
            Summary containing scanned, expired, and failed counts.
    """
    scanned = 0
    expired = 0
    failed = 0

    cutoff = timezone.now() - timezone.timedelta(
        days=OrderAdjustmentTaskConfig.RESPONSE_WINDOW_DAYS
    )

    queryset = OrderAdjustmentRequest.objects.filter(
        status="pending_client_response",
        created_at__lte=cutoff,
    ).select_related(
        "website",
        "order",
    )

    for adjustment_request in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            adjustment_request.status = "expired"
            adjustment_request.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )
            expired += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to expire stale adjustment.",
                extra={"adjustment_request_id": adjustment_request.pk},
            )

    return {
        "scanned": scanned,
        "expired": expired,
        "failed": failed,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_pending_adjustment_funding_reminders(
    self,
) -> dict[str, int]:
    """
    Remind clients about accepted adjustments that still need funding.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderAdjustmentFunding.objects.filter(
        status__in=[
            "not_started",
            "payment_request_created",
            "payment_intent_created",
            "partially_funded",
        ]
    ).select_related(
        "website",
        "adjustment_request",
        "adjustment_request__order",
    )

    for funding in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            order = funding.adjustment_request.order
            client = getattr(order, "client", None)
            if client is None:
                continue

            NotificationService.notify(
                event_key="order.adjustment.pending_funding_reminder",
                recipient=client,
                website=funding.website,
                context={
                    "funding_id": funding.pk,
                    "adjustment_request_id": funding.adjustment_request.pk,
                    "order_id": order.pk,
                },
                triggered_by=None,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send adjustment funding reminder.",
                extra={"funding_id": funding.pk},
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
def send_adjustment_staff_visibility_reminders(
    self,
) -> dict[str, int]:
    """
    Notify staff about open adjustment workflows that need attention.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderAdjustmentRequest.objects.filter(
        status__in=[
            "pending_client_response",
            "client_countered",
            "funding_pending",
        ]
    ).select_related(
        "website",
        "order",
    )

    for adjustment_request in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.adjustment.staff_visibility_reminder",
                recipient=None,
                website=adjustment_request.website,
                context={
                    "adjustment_request_id": adjustment_request.pk,
                    "order_id": adjustment_request.order.pk,
                    "status": adjustment_request.status,
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send adjustment staff reminder.",
                extra={"adjustment_request_id": adjustment_request.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }