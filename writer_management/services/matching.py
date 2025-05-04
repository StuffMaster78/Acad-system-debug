from django.db.models import Count, Q, F
from orders.models import OrderInterest
from writer_management.models import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()


def get_available_writers_for_order(order):
    """
    Retrieves writers who expressed interest in an order and have available slots.

    Args:
        order (Order): The order for which to find writers.

    Returns:
        QuerySet: Writers eligible for assignment.
    """
    # Get users who showed interest
    interested_writer_ids = OrderInterest.objects.filter(
        order=order
    ).values_list("writer_id", flat=True)

    # Filter writers with available slos
    eligible_writers = WriterProfile.objects.annotate(
        active_orders=Count(
            'user__assigned_orders',
            filter=Q(user__assigned_orders__status__in=["in_progress", "assigned"])
        )
    ).filter(
        user__id__in=interested_writer_ids,
        active_orders__lt=F("max_slots")
    )

    return User.objects.filter(id__in=eligible_writers.values_list("user_id", flat=True))