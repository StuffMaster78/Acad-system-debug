from django.db.models import Count, Q, F
from orders.models import Order, OrderInterest
from writer_management.models import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()

ACTIVE_ORDER_STATUSES = [
    "assigned", "in_progress", "revision_requested",
    "revision_in_progress", "revision_completed", 
    "completed", "ready_for_review", "ready_for_revision",
    "ready_for_completion"
]


class WriterAvailabilityService:
    @staticmethod
    def get_available_writers_for_order(order: Order):
        """
        Retrieve writers who:
        - Expressed interest in the given order
        - Have fewer active orders than their max_slots

        Returns:
            QuerySet[User]: Eligible users
        """
        interested_writer_ids = OrderInterest.objects.filter(
            order=order
        ).values_list("writer_id", flat=True)

        eligible_profiles = WriterProfile.objects.annotate(
            active_orders=Count(
                "user__assigned_orders",
                filter=Q(
                    user__assigned_orders__status__in=ACTIVE_ORDER_STATUSES
                )
            )
        ).filter(
            user_id__in=interested_writer_ids,
            active_orders__lt=F("max_slots")
        )

        return User.objects.filter(
            id__in=eligible_profiles.values_list("user_id", flat=True)
        ).order_by("username")