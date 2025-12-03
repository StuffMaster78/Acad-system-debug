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

        if order.status not in ('reviewed', 'rated', 'complete'):
            raise ValueError(
                f"Order {order_id} cannot be approved from state "
                f"{order.status}."
            )

        # Check if review and rating exist
        if not order.review:
            raise ValueError(f"Order {order_id} lacks a review.")

        if not order.rating:
            raise ValueError(f"Order {order_id} lacks a rating.")

        order.status = 'approved'
        save_order(order)
        
        # Award referral bonus when order is approved (first approved order only)
        self._award_referral_bonus(order)
        
        return order