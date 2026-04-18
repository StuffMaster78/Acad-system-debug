from __future__ import annotations

import logging

from celery import shared_task

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order import Order
from orders.models.orders.order_interest import OrderInterest

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_unstaffed_order_reminders(self) -> dict[str, int]:
    """
    Notify staff about staffing-ready orders that still have no active
    current assignment.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = Order.objects.filter(
        status="ready_for_staffing",
    ).select_related(
        "website",
        "client",
        "preferred_writer",
    ).prefetch_related(
        "assignments",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            assignments = getattr(order, "assignments", None)
            if assignments is None:
                continue

            has_current_assignment = assignments.filter(
                is_current=True
            ).exists()
            if has_current_assignment:
                continue

            NotificationService.notify(
                event_key="order.staffing.unstaffed_order_reminder",
                recipient=None,
                website=order.website,
                context={
                    "order_id": order.pk,
                    "preferred_writer_id": getattr(
                        getattr(order, "preferred_writer", None),
                        "pk",
                        None,
                    ),
                },
                triggered_by=None,
                is_broadcast=True,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send unstaffed order reminder.",
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
def expire_preferred_writer_invitations(self) -> dict[str, int]:
    """
    Expire pending preferred writer invitations that have crossed their
    configured response window.

    Notes:
        This task assumes OrderInterest has:
            - interest_type
            - status
            - created_at
        and that your service layer will later own the actual expiry
        mutation cleanly.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    from django.utils import timezone

    scanned = 0
    expired = 0
    failed = 0

    response_window_hours = 24
    cutoff = timezone.now() - timezone.timedelta(
        hours=response_window_hours
    )

    queryset = OrderInterest.objects.filter(
        interest_type="preferred_writer_invitation",
        status="pending",
        created_at__lte=cutoff,
    ).select_related(
        "website",
        "order",
        "writer",
    )

    for interest in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            interest.status = "expired"
            interest.reviewed_at = timezone.now()
            interest.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                    "updated_at",
                ]
            )

            order = interest.order
            order.preferred_writer_status = "expired"
            order.save(
                update_fields=[
                    "preferred_writer_status",
                    "updated_at",
                ]
            )
            expired += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to expire preferred writer invitation.",
                extra={"interest_id": interest.pk},
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
def fallback_expired_preferred_writer_orders_to_pool(
    self,
) -> dict[str, int]:
    """
    Move staffing-ready orders with expired preferred writer routing
    back to the pool.

    Returns:
        dict[str, int]:
            Processing summary.
    """
    scanned = 0
    moved = 0
    failed = 0

    queryset = Order.objects.filter(
        status="ready_for_staffing",
        preferred_writer_status="expired",
    ).select_related(
        "website",
        "client",
        "preferred_writer",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            order.visibility_mode = "pool"
            order.preferred_writer_status = "fallback_to_pool"
            order.save(
                update_fields=[
                    "visibility_mode",
                    "preferred_writer_status",
                    "updated_at",
                ]
            )
            moved += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to fallback expired preferred writer order to pool.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "moved": moved,
        "failed": failed,
    }