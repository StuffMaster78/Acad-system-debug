from __future__ import annotations

import logging
from typing import Any

from celery import shared_task
from django.utils import timezone

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order import Order
from orders.models.orders.order_interest import OrderInterest
from orders.models.orders.enums import (
    OrderStatus,
    PreferredWriterStatus,
)

logger = logging.getLogger(__name__)


class PreferredWriterTaskConfig:
    """
    Hold operational configuration for preferred writer task flows.
    """

    RESPONSE_WINDOW_HOURS = 24


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_pending_preferred_writer_reminders(self) -> dict[str, int]:
    """
    Remind preferred writers about pending invitations.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = OrderInterest.objects.filter(
        interest_type="preferred_writer_invitation",
        status="pending",
    ).select_related(
        "website",
        "order",
        "writer",
    )

    for interest in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            writer = getattr(interest, "writer", None)
            if writer is None:
                continue

            order = interest.order
            writer_deadline = getattr(order, "writer_deadline", None)
            writer_deadline_iso = (
                writer_deadline.isoformat()
                if writer_deadline is not None
                else None
            )

            NotificationService.notify(
                event_key="order.preferred_writer.pending_reminder",
                recipient=writer,
                website=interest.website,
                context={
                    "interest_id": interest.pk,
                    "order_id": order.pk,
                    "writer_deadline": writer_deadline_iso,
                },
                triggered_by=None,
            )
            reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send preferred writer reminder.",
                extra={"interest_id": interest.pk},
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
    Expire preferred writer invitations that crossed the response window.

    Returns:
        dict[str, int]:
            Summary containing scanned, expired, and failed counts.
    """
    scanned = 0
    expired = 0
    failed = 0

    cutoff = timezone.now() - timezone.timedelta(
        hours=PreferredWriterTaskConfig.RESPONSE_WINDOW_HOURS
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
            order.preferred_writer_status = PreferredWriterStatus.EXPIRED
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
    Move preferred writer orders with expired invitations back to pool.

    Returns:
        dict[str, int]:
            Summary containing scanned, moved, and failed counts.
    """
    scanned = 0
    moved = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.READY_FOR_STAFFING,
        preferred_writer_status=PreferredWriterStatus.EXPIRED,
    ).select_related(
        "website",
        "client",
        "preferred_writer",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            order.visibility_mode = "pool"
            order.preferred_writer_status = PreferredWriterStatus.FALLBACK_TO_POOL
            order.save(
                update_fields=[
                    "visibility_mode",
                    "preferred_writer_status",
                    "updated_at",
                ]
            )

            NotificationService.notify(
                event_key="order.preferred_writer.fallback_to_pool",
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
            moved += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to fallback preferred writer order to pool.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "moved": moved,
        "failed": failed,
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_preferred_writer_staff_visibility_reminders(
    self,
) -> dict[str, int]:
    """
    Notify staff about orders still stuck in preferred writer mode.

    Returns:
        dict[str, int]:
            Summary containing scanned, reminded, and failed counts.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.READY_FOR_STAFFING,
        visibility_mode="preferred_writer_only",
        preferred_writer_status=PreferredWriterStatus.INVITED,
    ).select_related(
        "website",
        "client",
        "preferred_writer",
    )

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            NotificationService.notify(
                event_key="order.preferred_writer.staff_visibility_reminder",
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
                "Failed to send preferred writer staff reminder.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }