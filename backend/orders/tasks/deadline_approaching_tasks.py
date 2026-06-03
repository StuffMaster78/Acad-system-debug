"""
Periodic task: notify writers when their order deadline is approaching.

Three tiers fire when the deadline falls inside a 1-hour window:
  • 24 h  — early heads-up
  •  6 h  — act now
  •  1 h  — final warning

Running this task every 30 minutes and using a 1-hour window per tier
guarantees each threshold is hit at least once even if a task run is
slightly delayed, while the NotificationService cooldown (seeded at
3600 s for order.deadline_approaching) prevents duplicate sends.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

log = logging.getLogger(__name__)

_TIERS: list[int] = [24, 6, 1]  # hours before deadline


@shared_task(
    name="orders.tasks.check_order_deadlines",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def check_order_deadlines(self) -> dict:
    from orders.models.orders import Order
    from orders.services.order_notification_service import OrderNotificationService

    now = timezone.now()
    notified = 0
    errors = 0

    active_statuses = ("in_progress", "qa_review")
    for hours in _TIERS:
        window_start = now + timedelta(hours=hours - 1)
        window_end   = now + timedelta(hours=hours)

        orders = (
            Order.objects
            .filter(
                status__in=active_statuses,
                writer_deadline__gt=window_start,
                writer_deadline__lte=window_end,
            )
            .select_related("website", "client")
            .only("pk", "topic", "status", "writer_deadline", "website", "client")
        )

        for order in orders.iterator(chunk_size=200):
            try:
                OrderNotificationService.notify_order_deadline_approaching(
                    order=order,
                    hours_remaining=hours,
                )
                notified += 1
            except Exception as exc:
                log.exception(
                    "check_order_deadlines: failed order=%s tier=%sh: %s",
                    order.pk, hours, exc,
                )
                errors += 1

    log.info("check_order_deadlines: notified=%d errors=%d", notified, errors)
    return {"notified": notified, "errors": errors}
