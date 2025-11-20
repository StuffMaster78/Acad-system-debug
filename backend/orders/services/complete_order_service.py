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
        # Order model uses is_paid, not payment_status
        is_paid = getattr(order, 'is_paid', False) or getattr(order, 'payment_status', None) == 'paid'
        if order.status != 'completed' or not is_paid:
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
        
        For unattributed orders, if completed by admin/superadmin, they become the client.

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

        if order.status not in ['in_progress', 'on_revision', 'reviewed', 'on_hold', 'submitted', 'under_editing']:
            raise ValueError(f"Order {order_id} cannot be completed from state {order.status}.")

        # For unattributed orders completed by admin/superadmin, set admin as client
        is_unattributed = order.client_id is None and (
            bool(getattr(order, 'external_contact_name', None)) or
            bool(getattr(order, 'external_contact_email', None))
        )
        
        if is_unattributed and user.role in ['admin', 'superadmin']:
            # Admin/superadmin becomes the client for unattributed orders
            order.client = user
            logger.info(f"Unattributed order {order_id} completed by {user.username}. Admin set as client.")
        
        order.status = 'completed'
        order.completed_by = user
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