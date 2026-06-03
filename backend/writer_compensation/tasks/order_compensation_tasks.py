from __future__ import annotations

import logging
from decimal import Decimal

from celery import shared_task

log = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
    name="writer_compensation.create_order_compensation_event",
)
def create_order_compensation_event(self, *, order_id: int) -> None:
    """
    Create a CompensationEvent for a completed order.

    Dispatched by the order post_save signal when status transitions to
    COMPLETED. Idempotent via idempotency_key — safe to retry.

    Skips silently (no retry) when:
    - Order is no longer completed (status changed between signal and task)
    - No current writer assigned
    - writer_compensation is zero

    Retries automatically (up to 3 times with backoff) on:
    - NoOpenWindowError (window may open soon)
    - Any other unexpected exception
    """
    from orders.models.orders import Order
    from writer_compensation.enums.compensation_enums import EventSource, EventType
    from writer_compensation.exceptions.exceptions import NoOpenWindowError, ZeroAmountError
    from writer_compensation.services.event_intake_service import EventIntakeService

    try:
        order = Order.objects.select_related("website").get(pk=order_id)
    except Order.DoesNotExist:
        log.warning("create_order_compensation_event: order %s not found — skip.", order_id)
        return

    if order.status != "completed":
        log.info(
            "create_order_compensation_event: order %s status=%s — skip.",
            order_id, order.status,
        )
        return

    writer = order.assigned_writer
    if writer is None:
        log.warning(
            "create_order_compensation_event: order %s has no assigned writer — skip.",
            order_id,
        )
        return

    amount = order.writer_compensation or Decimal("0.00")
    if amount <= 0:
        log.warning(
            "create_order_compensation_event: order %s writer_compensation=%s — skip.",
            order_id, amount,
        )
        return

    try:
        event, created = EventIntakeService.record(
            website=order.website,
            writer=writer,
            event_type=EventType.ORDER_EARNING,
            amount=amount,
            source=EventSource.ORDER,
            source_type="order",
            source_id=order.pk,
            title=f"Order #{order.pk}",
            notes=order.topic or "",
            idempotency_key=f"order_completion_{order.pk}",
        )
        if created:
            log.info(
                "create_order_compensation_event: created event %s for order %s writer %s amount %s.",
                event.pk, order_id, writer.pk, amount,
            )
        else:
            log.debug(
                "create_order_compensation_event: event already exists for order %s — idempotent skip.",
                order_id,
            )
    except ZeroAmountError:
        log.warning("create_order_compensation_event: order %s zero amount — skip.", order_id)
    except NoOpenWindowError as exc:
        log.warning(
            "create_order_compensation_event: order %s no open window (%s) — will retry.",
            order_id, exc,
        )
        raise  # triggers autoretry
