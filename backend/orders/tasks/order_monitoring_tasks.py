from __future__ import annotations

import logging
from typing import Any, cast

from celery import shared_task

from orders.models.orders.enums import OrderStatus
from orders.models import Order
from orders.services.order_monitoring_service import (
    OrderMonitoringService,
)
from orders.services.order_reminder_service import (
    OrderReminderService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def send_writer_acknowledgement_reminders(self) -> dict[str, int]:
    """
    Send reminders to writers who have not acknowledged active orders.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.IN_PROGRESS,
    ).select_related("website")

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            typed_order = cast(Any, order)
            assignments = getattr(typed_order, "assignments", None)
            if assignments is None:
                continue

            current_assignment = (
                assignments.filter(is_current=True)
                .select_related("writer")
                .first()
            )
            if current_assignment is None:
                continue

            was_sent = (
                OrderReminderService.send_writer_acknowledgement_reminder(
                    order=order,
                    writer=current_assignment.writer,
                    triggered_by=None,
                )
            )
            if was_sent:
                reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send writer acknowledgement reminder.",
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
def send_operational_writer_reminders(self) -> dict[str, int]:
    """
    Send writer reminders for critical and late in-progress orders.
    """
    scanned = 0
    reminded = 0
    failed = 0

    queryset = Order.objects.filter(
        status=OrderStatus.IN_PROGRESS,
    ).select_related("website")

    for order in queryset.iterator(chunk_size=200):
        scanned += 1
        try:
            operational_state = (
                OrderMonitoringService.build_operational_state(
                    order=order,
                )
            )
            if operational_state.state_label not in {"critical", "late"}:
                continue

            typed_order = cast(Any, order)
            assignments = getattr(typed_order, "assignments", None)
            if assignments is None:
                continue

            current_assignment = (
                assignments.filter(is_current=True)
                .select_related("writer")
                .first()
            )
            if current_assignment is None:
                continue

            was_sent = (
                OrderReminderService.send_operational_writer_reminder(
                    order=order,
                    writer=current_assignment.writer,
                    triggered_by=None,
                )
            )
            if was_sent:
                reminded += 1
        except Exception:
            failed += 1
            logger.exception(
                "Failed to send operational writer reminder.",
                extra={"order_id": order.pk},
            )

    return {
        "scanned": scanned,
        "reminded": reminded,
        "failed": failed,
    }