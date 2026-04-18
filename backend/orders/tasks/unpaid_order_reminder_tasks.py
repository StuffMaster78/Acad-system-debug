from __future__ import annotations

from celery import shared_task

from orders.models.orders.order import Order
from orders.services.unpaid_order_dispatch_service import (
    UnpaidOrderMessageDispatchService,
)
from orders.services.unpaid_order_message_service import (
    UnpaidOrderMessageService,
)


@shared_task
def schedule_unpaid_order_dispatches_for_order(order_id: int) -> int:
    """
    Create reminder dispatches for a single order if eligible.
    """
    order = Order.objects.select_related("website", "client").get(pk=order_id)
    return UnpaidOrderMessageService.schedule_due_dispatches_for_order(
        order=order,
    )


@shared_task
def process_due_unpaid_order_dispatches() -> int:
    """
    Process all due unpaid order reminder dispatches.
    """
    return UnpaidOrderMessageDispatchService.process_due_dispatches()