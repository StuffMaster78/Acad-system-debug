from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order
from celery import current_app
import logging
from referrals.models import Referral
from referrals.services.referral_service import ReferralService
from django.db import transaction

logger = logging.getLogger(__name__)

class CompleteOrderService:
    """
    Service to handle marking orders as completed.

    Methods:
        complete_order: Marks the specified order as completed.
    """
    
    allowed_roles = {"Writer", "Editor", "Support", "Admin", "Superadmin"}

    @staticmethod
    @transaction.atomic
    def _award_referral_bonus(order):
        """ Check if the order qualifies for a referral bonus and award it if applicable."""
        if order.status != 'completed' or order.payment_status != 'paid':
            return

        try:
            referral = Referral.objects.filter(
                referee=order.user,
                website=order.website
            ).first()
            if not referral:
                return

            service = ReferralService(referral)
            service.award_bonus()
        except Exception as e:
            logger.warning(f"Failed to award referral bonus for Order {order.id}: {str(e)}")

    def complete_order(self, order_id: int, user) -> Order:
        """
        Complete an order by its ID.

        Args:
            order_id (int): The ID of the order to complete.
            user (User): The user requesting the completion.

        Returns:
            Order: The updated order instance marked as completed.

        Raises:
            PermissionError: If the user does not have permission to complete the order.
            ValueError: If the order cannot be completed due to state.
        """
        order = get_order_by_id(order_id)

        # Permission Check
        if not user.is_staff and not user.groups.filter(name__in=self.allowed_roles).exists():
            raise PermissionError("User is not authorized to complete the order.")

        if order.status not in ['in_progress', 'on_revision' 'reviewed', 'on_hold']:
            raise ValueError(f"Order {order_id} cannot be completed from state {order.status}.")

        order.status = 'completed'
        save_order(order)

        self._award_referral_bonus(order)

        # Send notification via Celery
        if order.client:
            try:
                current_app.send_task(
                    "orders.tasks.send_order_completion_email",
                    args=[order.client.email, order.client.username, order.id],
                )
                logger.info(f"Order completion email task queued for Order {order_id}.")
            except Exception as e:
                logger.warning(f"Failed to queue completion email for Order {order_id}: {e}")

        # OrderActionLog.objects.create(
        #     order=order,
        #     performed_by=user,
        #     action="completed",
        #     notes="Order marked complete via CompleteOrderService"
        # )

        return order