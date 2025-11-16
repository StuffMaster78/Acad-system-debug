import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime


from authentication.models import AuditLog

logger = logging.getLogger(__name__)


def get_order_by_id(order_id, user=None, check_soft_deleted=True):
    """
    Retrieve an Order instance by its ID, with optional soft-delete check.

    Args:
        order_id (int): The primary key of the order.
        user (User, optional): The requesting user, for audit logging.
        check_soft_deleted (bool): Whether to exclude soft-deleted orders.

    Returns:
        Order: The retrieved order instance.

    Raises:
        Http404: If the order does not exist.
    """
    from users.models import User
    from orders.models import Order
    queryset = Order.objects.all()

    if check_soft_deleted and hasattr(Order, 'is_deleted'):
        queryset = queryset.filter(is_deleted=False)

    order = get_object_or_404(queryset, id=order_id)

    if user:
        _log_order_access(user, order)

    logger.debug(f"Order #{order.id} retrieved by user {user}")

    return order


def save_order(order, user=None, event=None, notes=None):
    """
    Save an order instance and optionally log the event.

    Args:
        order (Order): The order instance to save.
        user (User, optional): The user performing the action.
        event (str, optional): Description of the event for audit logging.
        notes (str, optional): Additional notes for the audit log.
    """
    order.updated_at = timezone.now()
    
    # Check if status_changed_at field exists before including it
    update_fields = ["status", "updated_at"]
    if hasattr(order, 'status_changed_at'):
        update_fields.append("status_changed_at")
    
    order.save(update_fields=update_fields)

    logger.info(f"Order #{order.id} saved. Status: {order.status}")

    if user and event:
        _log_order_event(user, order, event, notes)


def _log_order_event(user, order, event, notes=None):
    """
    Create an audit log entry for an order-related event.

    Args:
        user (User): The acting user.
        order (Order): The order affected.
        event (str): A short description of the event.
        notes (str, optional): Extra detail for the log.
    """
    AuditLog.objects.create(
        user=user,
        action=event,
        related_object=order,
        notes=notes or f"Status changed to {order.status}"
    )


def _log_order_access(user, order):
    """
    Log when a user views or accesses an order.

    Args:
        user (User): The user accessing the order.
        order (Order): The order being accessed.
    """
    AuditLog.objects.create(
        user=user,
        action="order_viewed",
        related_object=order,
        notes=f"Viewed order #{order.id}"
    )


def get_orders_by_status_older_than(status: str, cutoff_date: datetime):
    """
    Return QuerySet of orders with given status older than cutoff_date.
    """
    from orders.models import Order
    return Order.objects.filter(status=status, updated_at__lt=cutoff_date)
