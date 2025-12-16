from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class ApproveOrderService:
    """
    Service to approve an order after review and rating.

    Methods:
        approve_order: Transitions the order to 'approved' state if eligible.
    """

    @staticmethod
    @transaction.atomic
    def _award_referral_bonus(order):
        """
        Award referral bonus when order is approved.
        A client only becomes eligible for referral rewards after ordering 
        and approving their first order to avoid abuse.
        """
        if order.status != 'approved':
            return

        try:
            from referrals.models import Referral
            from referrals.services.referral_service import ReferralService
            
            # Get the client from the order
            order_client = getattr(order, 'client', None) or getattr(order, 'user', None)
            if not order_client:
                return
            
            # Find referral for this client
            referral = Referral.objects.filter(
                referee=order_client,
                website=order.website,
                is_deleted=False
            ).first()
            
            if not referral:
                return

            # Check if this is the first approved order
            previous_approved_orders = order_client.orders_as_client.exclude(id=order.id).filter(status='approved')
            if previous_approved_orders.exists():
                # Not the first approved order, don't award bonus
                return

            # Award the bonus
            service = ReferralService(referral)
            service.award_bonus()
        except Exception as e:
            logger.warning(f"Failed to award referral bonus for Order {order.id}: {str(e)}")

    def approve_order(self, order_id: int) -> Order:
        """
        Approve an order by its ID.

        Args:
            order_id (int): The ID of the order to approve.

        Returns:
            Order: The updated order in 'approved' state.

        Raises:
            ValueError: If the order cannot be approved due to its state
                        or missing review/rating.
        """
        order = get_order_by_id(order_id)

        # Check valid transitions - 'approved' can be reached from 'reviewed' according to VALID_TRANSITIONS
        from orders.services.status_transition_service import VALID_TRANSITIONS
        current_status = order.status
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
        
        if 'approved' not in allowed_transitions:
            # Try to transition through intermediate states if needed
            if 'rated' in allowed_transitions and current_status != 'rated':
                # First transition to rated, then to approved
                from orders.services.transition_helper import OrderTransitionHelper
                OrderTransitionHelper.transition_order(
                    order,
                    'rated',
                    user=None,
                    reason="Transitioning to rated before approval",
                    action="transition_to_rated",
                    is_automatic=True,
                    skip_payment_check=True,
                    metadata={"intermediate_step": True}
                )
            elif current_status not in ('reviewed', 'rated'):
                raise ValueError(
                    f"Order {order_id} cannot be approved from state '{current_status}'. "
                    f"Order must be in 'reviewed' or 'rated' status. "
                    f"Allowed transitions from '{current_status}': {', '.join(allowed_transitions)}"
                )

        # Check if review and rating exist
        if not order.review:
            raise ValueError(f"Order {order_id} lacks a review.")

        if not order.rating:
            raise ValueError(f"Order {order_id} lacks a rating.")

        # Use unified transition helper to move to approved
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            order,
            'approved',
            user=None,  # System/automatic approval after review
            reason="Order approved after review and rating",
            action="approve_order",
            is_automatic=True,
            skip_payment_check=True,  # Payment already validated
            metadata={
                "has_review": bool(order.review),
                "has_rating": bool(order.rating),
            }
        )
        
        # Award referral bonus when order is approved (first approved order only)
        self._award_referral_bonus(order)
        
        return order