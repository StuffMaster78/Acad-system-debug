from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from orders.models import Order
from notifications_system.utils import send_notification  # Assuming this exists

User = get_user_model()

@transaction.atomic
def assign_writer(order: Order, writer_id: int) -> Order:
    """
    Assigns a writer to an order and updates its status.

    Args:
        order (Order): The order instance to update.
        writer_id (int): The ID of the writer to assign.

    Returns:
        Order: The updated order with an assigned writer.
    """
    if order.assigned_writer:
        raise ValidationError("Order is already assigned to a writer.")

    try:
        writer = User.objects.get(id=writer_id, role='writer', is_active=True)
    except User.DoesNotExist:
        raise ObjectDoesNotExist(f"Writer with ID {writer_id} does not exist or is not active.")

    order.assigned_writer = writer
    order.status = "in_progress"  # Update as per your actual status codes
    order.save()

    send_notification(
        writer,
        "New Order Assigned",
        f"You've been assigned to Order #{order.id}."
    )
    send_notification(
        order.client,
        "Writer Assigned",
        f"A writer has been assigned to your Order #{order.id}."
    )

    return order


@transaction.atomic
def unassign_writer(order: Order) -> Order:
    """
    Unassigns the current writer from an order and sets it back to available.

    Args:
        order (Order): The order to update.

    Returns:
        Order: The updated order with no assigned writer.
    """
    if not order.assigned_writer:
        raise ValidationError("Order is not currently assigned to any writer.")

    writer = order.assigned_writer
    order.assigned_writer = None
    order.status = "available"  # Update as needed for your system
    order.save()

    send_notification(
        writer,
        "Order Unassigned",
        f"You've been unassigned from Order #{order.id}."
    )
    send_notification(
        order.client,
        "Writer Unassigned",
        f"The writer was unassigned from your Order #{order.id} and it's now available again."
    )

    return order