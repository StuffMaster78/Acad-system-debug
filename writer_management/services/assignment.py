"""
Service layer for assigning writers to orders.
"""

from django.db import transaction
from django.utils import timezone
from orders.models import Order
from writer_management.models import WriterProfile
from django.core.exceptions import ObjectDoesNotExist

def get_available_writers(subject=None, limit=5):
    """
    Returns available writers, optionally filtered by subject expertise.

    Args:
        subject (str, optional): If provided, filters by matching subject expertise.
        limit (int): Max number of writers to return.

    Returns:
        QuerySet: A queryset of WriterProfile instances.
    """
    qs = WriterProfile.objects.filter(
        is_active=True,
        is_available=True,
        user__is_active=True
    )

    if subject:
        qs = qs.filter(subjects__icontains=subject)

    return qs.order_by('-rating')[:limit]


@transaction.atomic
def assign_writer_to_order(order, writer=None):
    """
    Assigns a writer to an order, either the one provided or the best available.

    Args:
        order (Order): The order to be assigned.
        writer (User, optional): If provided, assign this writer directly.

    Returns:
        Order: The updated order.

    Raises:
        Exception: If no suitable writer is found.
    """
    if writer is None:
        subject = order.subject if hasattr(order, 'subject') else None
        available_writers = get_available_writers(subject)

        if not available_writers.exists():
            raise Exception("No available writers for this order.")

        writer = available_writers.first().user  # Get the actual User instance

    order.assigned_writer = writer
    order.status = "in_progress"
    order.assigned_at = timezone.now()
    order.save()

    # Log it or notify
    # notify_writer_assignment(writer, order)
    # ActivityLog.objects.create(...)

    return order