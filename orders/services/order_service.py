from django.db import transaction
from orders.exceptions import TransitionNotAllowed
from discounts.services.engine import DiscountEngine
from discounts.services.hints import DiscountHintService
from discounts.services.usage import DiscountUsageService
from django.core.exceptions import ValidationError
from notifications_system.services.send_notification import notify_admin_of_error
import logging
from discounts.services.suggestions import DiscountSuggestionService
from orders.services.order_utils import _get_order, save_order

logger = logging.getLogger(__name__)

class OrderService:
    """
    Service class to handle the order lifecycle and state transitions.
    """
    @staticmethod
    def create_order(user, topic, deadline, **kwargs):
        """
        Creates a new order and evaluates urgency to assign the correct
        initial status.
        """
        from django.apps import apps
        from orders.models import OrderStatus
        from orders.services.utils import check_if_urgent
    
        Order = apps.get_model('orders', 'Order')

        status = (
            OrderStatus.CRITICAL
            if deadline and check_if_urgent(deadline)
            else OrderStatus.CREATED
        )

        order = Order.objects.create(
            user=user,
            topic=topic,
            deadline=deadline,
            status=status,
            **kwargs
        )
        return order

    @staticmethod
    @transaction.atomic
    def transition_to_pending(order_id):
        """
        Transition order to 'pending' state if allowed.
        """
        order = _get_order(order_id)
        if order.status not in ['unpaid', 'available']:
            raise TransitionNotAllowed(
                "Order cannot be moved to 'pending' from the current status."
            )
        order.status = 'pending'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def put_on_hold(order_id):
        """
        Puts the order on hold if it is in 'assigned' state.
        """
        order = _get_order(order_id)
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be put on hold."
            )
        order.status = 'on_hold'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def resume_order(order_id):
        """
        Resume an order from on hold status.
        """
        order = _get_order(order_id)
        if order.status != 'on_hold':
            raise TransitionNotAllowed(
                "Only orders on hold can be resumed."
            )
        order.status = 'assigned'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def assign_writer(order_id, writer):
        """
        Assign a writer to the order if it is in 'pending' state.
        """
        order = _get_order(order_id)
        if order.status != 'pending':
            raise TransitionNotAllowed(
                "Order must be in 'pending' state to assign a writer."
            )
        order.status = 'assigned'
        order.writer = writer  # Assuming there is a `writer` field on the `Order`.
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def complete_order(order_id, completed_by=None, completion_notes=None):
        """
        Mark the order as complete if it is in 'assigned' state.
        """
        order = _get_order(order_id)
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' before it can be completed."
            )
        
        # If an admin/support is completing the order manually, record who did it
        if completed_by:
            order.completed_by = completed_by
            order.completion_notes = (
                completion_notes or "Completed manually by support/admin."
            )
        order.status = 'completed'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def dispute_order(order_id):
        """
        Mark the order as disputed if it is in 'assigned' or 'revision' state.
        """
        order = _get_order(order_id)
        if order.status not in ['assigned', 'revision']:
            raise TransitionNotAllowed(
                "Order must be in 'assigned' or 'revision' state to dispute."
            )
        order.status = 'disputed'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def approve_order(order_id):
        """
        Approve the order once completed.
        """
        order = _get_order(order_id)
        if order.status != 'completed':
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be approved."
            )
        order.status = 'approved'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id):
        """
        Cancel the order if it is not in 'completed' or 'archived' state.
        """
        order = _get_order(order_id)
        if order.status in ['completed', 'archived']:
            raise TransitionNotAllowed(
                "Order cannot be cancelled once it is completed or archived."
            )
        order.status = 'cancelled'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def archive_order(order_id):
        """
        Archive the order once it is completed.
        """
        order = _get_order(order_id)
        if order.status != 'completed':
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be archived."
            )
        order.status = 'archived'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def late_order(order_id):
        """
        Mark the order as late if it is in 'assigned' state.
        """
        order = _get_order(order_id)
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked as late."
            )
        order.status = 'late'
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def revision_order(order_id):
        """
        Mark the order for revision if it is in 'assigned' state.
        """
        order = _get_order(order_id)
        if order.status != 'assigned':
            raise TransitionNotAllowed(
                "Order must be 'assigned' to be marked for revision."
            )
        order.status = 'revision'
        save_order(order)
        return order
    
        # New State: REVIEWED
    @staticmethod
    @transaction.atomic
    def review_order(order_id):
        """
        Transition the order to the 'reviewed' state.
        
        The order must be in the 'completed' state before it can be reviewed.
        Once reviewed, the status of the order is updated to 'reviewed'.
        
        Args:
            order_id (int): The ID of the order to be reviewed.
        
        Returns:
            Order: The updated order with the status set to 'reviewed'.
        
        Raises:
            TransitionNotAllowed: If the order is not in the 'completed' state.
        """
        order = _get_order(order_id)
        if order.status != 'completed':
            raise TransitionNotAllowed(
                "Order must be 'completed' before it can be reviewed."
            )
        order.status = 'reviewed'
        save_order(order)
        return order

    # New State: RATED
    @staticmethod
    @transaction.atomic
    def rate_order(order_id, rating):
        """
        Transition the order to the 'rated' state with a provided rating.
        
        The order must be in the 'reviewed' state before it can be rated.
        The rating must be a value between 1 and 5. Once rated, the order's 
        status is updated to 'rated', and the rating is saved.
        
        Args:
            order_id (int): The ID of the order to be rated.
            rating (int): The rating value for the order, between 1 and 5.
        
        Returns:
            Order: The updated order with the status set to 'rated' and the 
            assigned rating.
        
        Raises:
            TransitionNotAllowed: If the order is not in the 'reviewed' state.
            ValueError: If the rating is not between 1 and 5.
        """
        order = _get_order(order_id)
        if order.status != 'reviewed':
            raise TransitionNotAllowed(
                "Order must be 'reviewed' before it can be rated."
            )
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        order.status = 'rated'
        order.rating = rating  # Assuming `rating` field exists on the `Order`.
        save_order(order)
        return order

    
    @staticmethod
    @transaction.atomic
    def apply_discounts_to_order(order_id, codes: list[str], user):
        """
        Applies discount codes to an order.
        """
        order = _get_order(order_id)
        try:
            discounts = DiscountEngine.fetch_by_codes(codes, order.website)
            applicator = DiscountEngine(order, user, discounts)
            result = applicator.apply_discounts()

            DiscountUsageService.track(discounts, order, user)

            hint = DiscountHintService.get_stackable_hint(codes, order.website)
            if hint:
                result["stackable_hint"] = hint

            logger.info(f"Applied {len(discounts)} discounts to order {order.id} "
                        f"for user {user.id}")
            return result

        except ValidationError as ve:
            order.refresh_from_db()
            logger.warning(f"Discount validation error for order {order.id}: "
                           f"{str(ve)}")
            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            return {
                "final_price": float(order.total_price),
                "discounts_applied": [],
                "errors": [str(ve)],
                "stackable_hint": None,
                "suggested_discounts": suggestions
            }

        except Exception as e:
            logger.exception(f"Unexpected error during discount application on order "
                             f"{order.id}: {str(e)}")
            notify_admin_of_error(str(e))
            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            return {
                "final_price": float(order.total_price),
                "discounts_applied": [],
                "errors": ["Unexpected error occurred."],
                "codes_attempted": codes,
                "stackable_hint": None,
                "suggested_discounts": suggestions
            }
