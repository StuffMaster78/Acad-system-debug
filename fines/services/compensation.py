from decimal import Decimal
from django.db import transaction
from orders.models import Order


def adjust_writer_compensation(order: Order, amount_change: Decimal) -> None:
    """Adjust the writer's compensation for an order by a specified amount.

    Args:
        order (Order): The order whose writer compensation is adjusted.
        amount_change (Decimal): The amount to add (positive) or subtract (negative).

    Raises:
        AttributeError: If the order does not have 'writer_compensation' field.

    Returns:
        None
    """
    if not hasattr(order, "writer_compensation"):
        raise AttributeError("Order model missing 'writer_compensation' field.")

    with transaction.atomic():
        new_comp = order.writer_compensation + amount_change

        # Prevent negative compensation
        order.writer_compensation = max(new_comp, Decimal("0.00"))
        order.save(update_fields=["writer_compensation"])