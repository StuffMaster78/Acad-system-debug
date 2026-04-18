from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
import logging
from typing import Optional, Union

logger = logging.getLogger(__name__)


class InvalidOrderTransition(Exception):
    """
    Raised when an order cannot be transitioned to the desired status.
    """
    pass


def _get_order(order_id: Union[int, str]):
    """
    Returns the Order instance for the given ID.

    Args:
        order_id (int | str): The ID of the order.

    Returns:
        Order: The order instance.

    Raises:
        ObjectDoesNotExist: If the order is not found.
    """
    Order = apps.get_model("orders", "Order")
    return Order.objects.get(id=order_id)


def save_order(order, fields: Optional[list[str]] = None):
    """
    Saves the order instance with specified fields.

    Args:
        order (Order): The order instance to save.
        fields (list[str], optional): Fields to update. Defaults to ["status"].
    """
    order.save(update_fields=fields or ["status"])
    logger.debug(
        f"Saved order {order.id} with fields {fields or ['status']}"
    )


def transition_order_status(order_id: Union[int, str], to_status: str,
                            allowed_from: list[str]):
    """
    Handles safe state transition of an order.

    Args:
        order_id (int | str): ID of the order.
        to_status (str): Status to transition to.
        allowed_from (list[str]): Allowed current statuses.

    Returns:
        Order: Updated order instance.

    Raises:
        InvalidOrderTransition: If transition is not allowed.
    """
    order = _get_order(order_id)
    if order.status not in allowed_from:
        msg = (f"Cannot transition order {order.id} from {order.status} "
               f"to {to_status}. Allowed: {allowed_from}")
        logger.warning(msg)
        raise InvalidOrderTransition(msg)

    order.status = to_status
    save_order(order)
    logger.info(f"Order {order.id} transitioned to {to_status}")
    return order