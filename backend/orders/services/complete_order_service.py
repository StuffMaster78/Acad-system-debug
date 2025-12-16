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
        """
        NOTE: Referral bonuses are now awarded when orders are APPROVED, not completed.
        This method is kept for backward compatibility but should not award bonuses.
        A client only becomes eligible for referral rewards after ordering 
        and approving their first order to avoid abuse.
        """
        # Referral bonuses are now awarded in ApproveOrderService
        # This method is kept for backward compatibility but does nothing
        return

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

        # Check valid transitions - 'completed' can be reached from 'rated' or 'approved'
        from orders.services.status_transition_service import VALID_TRANSITIONS
        from orders.services.transition_helper import OrderTransitionHelper
        
        current_status = order.status
        target_status = 'completed'
        
        # Check if direct transition to completed is allowed
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
        
        # For unattributed orders completed by admin/superadmin, set admin as client
        is_unattributed = order.client_id is None and (
            bool(getattr(order, 'external_contact_name', None)) or
            bool(getattr(order, 'external_contact_email', None))
        )
        
        if is_unattributed and user.role in ['admin', 'superadmin']:
            # Admin/superadmin becomes the client for unattributed orders
            order.client = user
            logger.info(f"Unattributed order {order_id} completed by {user.username}. Admin set as client.")
        
        order.completed_by = user
        save_order(order)
        
        # If direct transition to completed is not allowed, try to go through intermediate states
        if target_status not in allowed_transitions:
            # Try to transition through 'rated' first (which allows transition to 'completed')
            if 'rated' in allowed_transitions:
                # First transition to rated
                OrderTransitionHelper.transition_order(
                    order,
                    'rated',
                    user=user,
                    reason="Transitioning to rated before completion",
                    action="transition_to_rated",
                    is_automatic=False,
                    skip_payment_check=True,
                    metadata={"intermediate_step": True}
                )
                # Then transition to completed
                OrderTransitionHelper.transition_order(
                    order,
                    'completed',
                    user=user,
                    reason="Order marked as completed",
                    action="complete_order",
                    is_automatic=False,
                    skip_payment_check=True,
                    metadata={
                        "completed_by_id": user.id,
                        "is_unattributed": is_unattributed,
                    }
                )
            elif 'approved' in allowed_transitions:
                # Try approved -> completed (approved can go directly to completed)
                OrderTransitionHelper.transition_order(
                    order,
                    'approved',
                    user=user,
                    reason="Transitioning to approved before completion",
                    action="transition_to_approved",
                    is_automatic=False,
                    skip_payment_check=True,
                    metadata={"intermediate_step": True}
                )
                # Then transition to completed (approved -> completed is valid)
                OrderTransitionHelper.transition_order(
                    order,
                    'completed',
                    user=user,
                    reason="Order marked as completed",
                    action="complete_order",
                    is_automatic=False,
                    skip_payment_check=True,
                    metadata={
                        "completed_by_id": user.id,
                        "is_unattributed": is_unattributed,
                    }
                )
            else:
                raise ValueError(
                    f"Cannot complete order from status '{current_status}'. "
                    f"Order must be in 'rated' or 'approved' status to be completed. "
                    f"Allowed transitions from '{current_status}': {', '.join(allowed_transitions)}"
                )
        else:
            # Direct transition is allowed
            OrderTransitionHelper.transition_order(
                order,
                'completed',
                user=user,
                reason="Order marked as completed",
                action="complete_order",
                is_automatic=False,
                skip_payment_check=True,  # Payment already validated
                metadata={
                    "completed_by_id": user.id,
                    "is_unattributed": is_unattributed,
                }
            )

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