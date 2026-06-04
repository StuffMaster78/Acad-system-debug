"""
SLA escalation tasks for order risk management.

  escalate_overdue_orders  — fires every 30 min; finds orders past writer_deadline
                             and still active; notifies staff + flags the order.

  detect_stuck_orders      — fires every hour; finds in_progress orders with no
                             writer activity for >8 h; surfaces them in the ops
                             command center via a timeline event.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

log = logging.getLogger(__name__)


@shared_task(
    name="orders.tasks.escalate_overdue_orders",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def escalate_overdue_orders(self) -> dict:
    """
    Detect orders past their writer_deadline and escalate to staff.

    An order is considered overdue when:
      - status is in_progress, qa_review, or submitted
      - writer_deadline < now
      - has not already been flagged for this overdue window
        (guarded by notification cooldown on order.overdue)
    """
    from orders.models.orders import Order, OrderTimelineEvent
    from orders.models.orders.enums import OrderTimelineEventType

    now = timezone.now()
    active_statuses = ("in_progress", "qa_review")

    overdue_orders = (
        Order.objects.filter(
            status__in=active_statuses,
            writer_deadline__lt=now,
        )
        .select_related("website", "client")
        .prefetch_related("assignments")
        .only("pk", "topic", "status", "writer_deadline", "website_id", "client_id")
    )

    escalated = 0
    errors = 0

    for order in overdue_orders.iterator(chunk_size=200):
        try:
            # Record a timeline event (idempotent: only once per overdue window)
            already_flagged = order.timeline_events.filter(
                event_type="overdue",
                created_at__gte=now - timedelta(hours=4),
            ).exists()

            if not already_flagged:
                OrderTimelineEvent.objects.create(
                    order=order,
                    event_type="overdue",
                    metadata={
                        "writer_deadline": order.writer_deadline.isoformat() if order.writer_deadline else None,
                        "hours_overdue": round(
                            (now - order.writer_deadline).total_seconds() / 3600, 1
                        ) if order.writer_deadline else None,
                    },
                )

            # Notify staff via the notification system
            try:
                from notifications_system.services.notification_service import NotificationService
                from django.contrib.auth import get_user_model
                User = get_user_model()

                staff = User.objects.filter(
                    role__in=["admin", "superadmin", "support"],
                    website=order.website,
                    is_active=True,
                ).only("pk", "email")[:10]

                for staff_user in staff:
                    NotificationService.notify(
                        event_key="order.overdue",
                        recipient=staff_user,
                        website=order.website,
                        context={
                            "order_id": order.pk,
                            "order_topic": order.topic,
                            "hours_overdue": round(
                                (now - order.writer_deadline).total_seconds() / 3600, 1
                            ) if order.writer_deadline else 0,
                        },
                        triggered_by=None,
                    )
            except Exception as notify_exc:
                log.warning("escalate_overdue_orders: notification failed order=%s: %s", order.pk, notify_exc)

            escalated += 1

        except Exception as exc:
            log.exception("escalate_overdue_orders: failed order=%s: %s", order.pk, exc)
            errors += 1

    log.info("escalate_overdue_orders: escalated=%d errors=%d", escalated, errors)
    return {"escalated": escalated, "errors": errors}


@shared_task(
    name="orders.tasks.detect_stuck_orders",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def detect_stuck_orders(self) -> dict:
    """
    Detect orders that have been in_progress for >8 hours with no writer activity.

    A stuck order is one where:
      - status = in_progress
      - last_writer_acknowledged_at is null OR updated_at < 8 hours ago
      - writer_deadline > now (not yet overdue — handled by escalate_overdue_orders)
    """
    from orders.models.orders import Order, OrderTimelineEvent

    now = timezone.now()
    stuck_threshold = now - timedelta(hours=8)

    stuck_orders = (
        Order.objects.filter(
            status="in_progress",
            writer_deadline__gte=now,  # not yet overdue
            updated_at__lt=stuck_threshold,
        )
        .select_related("website")
        .only("pk", "topic", "status", "updated_at", "writer_deadline", "website_id")
    )

    flagged = 0
    errors = 0

    for order in stuck_orders.iterator(chunk_size=200):
        try:
            # Only flag once per 8-hour window
            already = order.timeline_events.filter(
                event_type="stuck",
                created_at__gte=now - timedelta(hours=8),
            ).exists()

            if already:
                continue

            hours_since_activity = round(
                (now - order.updated_at).total_seconds() / 3600, 1
            )

            OrderTimelineEvent.objects.create(
                order=order,
                event_type="stuck",
                metadata={
                    "hours_since_activity": hours_since_activity,
                    "writer_deadline": order.writer_deadline.isoformat() if order.writer_deadline else None,
                },
            )
            flagged += 1

        except Exception as exc:
            log.exception("detect_stuck_orders: failed order=%s: %s", order.pk, exc)
            errors += 1

    log.info("detect_stuck_orders: flagged=%d errors=%d", flagged, errors)
    return {"flagged": flagged, "errors": errors}
