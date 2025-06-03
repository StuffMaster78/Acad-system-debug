from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.apps import apps
import logging
from order_configs.models import CriticalDeadlineSetting
from datetime import datetime, timedelta
from orders.exceptions import TransitionNotAllowed
from orders.models import OrderStatus, Order
from orders.services.order_utils import _get_order, save_order
from discounts.services.discount_engine import DiscountEngine
from discounts.services.discount_hints import DiscountHintService
from discounts.services.discount_suggestions import DiscountSuggestionService
from discounts.services.discount_usage_tracker import DiscountUsageTracker
from notifications_system.services.send_notification import notify_admin_of_error

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class handling order lifecycle, state transitions, and discount
    applications. Uses `OrderStatus` enums for status management.
    """

    @staticmethod
    def create_order(user, topic: str, deadline: Optional[str], **kwargs) -> Order:
        """
        Create a new order and assign initial status based on urgency.

        Args:
            user: The user placing the order.
            topic: The topic of the order.
            deadline: Optional deadline for the order.
            **kwargs: Additional fields for the order.

        Returns:
            Order: The newly created Order instance.
        """
        from orders.services.utils import check_if_urgent

        status = (
            OrderStatus.CRITICAL
            if deadline and check_if_urgent(deadline)
            else OrderStatus.CREATED
        )
        order = Order.objects.create(
            user=user,
            topic=topic,
            deadline=deadline,
            status=status.value,
            **kwargs,
        )
        return order

    @staticmethod
    def _assert_status(order: Order, allowed_statuses: List[OrderStatus]) -> None:
        """
        Helper to assert order's current status is in allowed_statuses.

        Args:
            order: The order to check.
            allowed_statuses: List of allowed OrderStatus enums.

        Raises:
            TransitionNotAllowed: If order.status is not in allowed_statuses.
        """
        if OrderStatus(order.status) not in allowed_statuses:
            allowed_names = [status.name for status in allowed_statuses]
            raise TransitionNotAllowed(
                f"Transition not allowed from status '{order.status}'. "
                f"Allowed statuses: {allowed_names}"
            )

    @staticmethod
    @transaction.atomic
    def transition_to_pending(order_id: int) -> Order:
        """
        Transition order to 'PENDING' if current status allows it.

        Args:
            order_id: ID of the order.

        Returns:
            Order: The updated order.

        Raises:
            TransitionNotAllowed: If current status disallows transition.
        """
        order = _get_order(order_id)
        allowed = [OrderStatus.UNPAID, OrderStatus.AVAILABLE]
        OrderService._assert_status(order, allowed)
        order.status_enum = OrderStatus.PENDING
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def put_on_hold(order_id: int) -> Order:
        """
        Put order on hold if it is currently 'ASSIGNED'.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'ON_HOLD' status.

        Raises:
            TransitionNotAllowed: If order is not 'ASSIGNED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.ON_HOLD
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def resume_order(order_id: int) -> Order:
        """
        Resume an order from 'ON_HOLD' to 'ASSIGNED'.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'ASSIGNED' status.

        Raises:
            TransitionNotAllowed: If order is not 'ON_HOLD'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ON_HOLD])
        order.status_enum = OrderStatus.ASSIGNED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def assign_writer(order_id: int, writer) -> Order:
        """
        Assign a writer to an order in 'PENDING' status.

        Args:
            order_id: ID of the order.
            writer: The writer to assign.

        Returns:
            Order: Updated order with 'ASSIGNED' status and writer set.

        Raises:
            TransitionNotAllowed: If order is not 'PENDING'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.PENDING])
        order.status_enum = OrderStatus.ASSIGNED
        order.writer = writer
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def complete_order(
        order_id: int,
        completed_by: Optional[Any] = None,
        completion_notes: Optional[str] = None,
    ) -> Order:
        """
        Mark an order as 'COMPLETED' from 'ASSIGNED' status.

        Args:
            order_id: ID of the order.
            completed_by: Optional user who completed the order.
            completion_notes: Optional notes regarding completion.

        Returns:
            Order: Updated order with 'COMPLETED' status.

        Raises:
            TransitionNotAllowed: If order is not 'ASSIGNED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])

        if completed_by:
            order.completed_by = completed_by
            order.completion_notes = completion_notes or "Completed manually."
        order.status_enum = OrderStatus.COMPLETED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def dispute_order(order_id: int) -> Order:
        """
        Mark an order as 'DISPUTED' from 'ASSIGNED' or 'REVISION'.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'DISPUTED' status.

        Raises:
            TransitionNotAllowed: If order status not allowed.
        """
        order = _get_order(order_id)
        allowed = [OrderStatus.ASSIGNED, OrderStatus.REVISION]
        OrderService._assert_status(order, allowed)
        order.status_enum = OrderStatus.DISPUTED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def approve_order(order_id: int) -> Order:
        """
        Approve an order in 'COMPLETED' status.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'APPROVED' status.

        Raises:
            TransitionNotAllowed: If order not 'COMPLETED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.COMPLETED])
        order.status_enum = OrderStatus.APPROVED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int) -> Order:
        """
        Cancel an order unless it's already 'COMPLETED' or 'ARCHIVED'.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'CANCELLED' status.

        Raises:
            TransitionNotAllowed: If order status disallows cancellation.
        """
        order = _get_order(order_id)
        disallowed = [OrderStatus.COMPLETED, OrderStatus.ARCHIVED]
        if OrderStatus(order.status) in disallowed:
            raise TransitionNotAllowed(
                "Order cannot be cancelled once completed or archived."
            )
        order.status_enum = OrderStatus.CANCELLED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def archive_order(order_id: int) -> Order:
        """
        Archive an order in 'COMPLETED' status.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'ARCHIVED' status.

        Raises:
            TransitionNotAllowed: If order not 'COMPLETED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.COMPLETED])
        order.status_enum = OrderStatus.ARCHIVED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def late_order(order_id: int) -> Order:
        """
        Mark an order 'LATE' from 'ASSIGNED' status.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'LATE' status.

        Raises:
            TransitionNotAllowed: If order not 'ASSIGNED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.LATE
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def revision_order(order_id: int) -> Order:
        """
        Mark an order for 'REVISION' from 'ASSIGNED' status.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'REVISION' status.

        Raises:
            TransitionNotAllowed: If order not 'ASSIGNED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.REVISION
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def review_order(order_id: int) -> Order:
        """
        Transition order to 'REVIEWED' from 'COMPLETED' status.

        Args:
            order_id: ID of the order.

        Returns:
            Order: Updated order with 'REVIEWED' status.

        Raises:
            TransitionNotAllowed: If order not 'COMPLETED'.
        """
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.COMPLETED])
        order.status_enum = OrderStatus.REVIEWED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def apply_discounts_to_order(order_id: int, codes: List[str], user) -> Dict[str, Any]:
        """
        Apply multiple discount codes to an order atomically.

        Args:
            order_id (int): The ID of the order.
            codes (List[str]): Discount codes to apply.
            user: The user applying the discounts.

        Returns:
            Dict[str, Any]: Result with final price, discounts applied, errors,
                            stackable hint, suggested discounts, attempted codes.
        """
        order = _get_order(order_id)
        result: Dict[str, Any] = {
            "final_price": float(order.total_price),
            "discounts_applied": [],
            "errors": [],
            "stackable_hint": None,
            "suggested_discounts": [],
            "codes_attempted": codes,
        }

        try:
            discounts = DiscountEngine.fetch_by_codes(codes, order.website)
            applicator = DiscountEngine(order, user, discounts)

            discount_result = applicator.apply_discounts()

            result.update({
                "final_price": discount_result.get("final_price", 
                                                result["final_price"]),
                "discounts_applied": discount_result.get("discounts_applied", []),
                "errors": discount_result.get("errors", []),
            })

            DiscountUsageTracker.track_multiple(discounts, order, user)

            hint = DiscountHintService.get_stackable_hint(codes, order.website)
            if hint:
                result["stackable_hint"] = hint

            logger.info(
                f"User {user.id} applied discounts {codes} to order {order.id} "
                f"final price {result['final_price']}"
            )

            return result

        except ValidationError as ve:
            order.refresh_from_db()
            logger.warning(f"Discount validation failed on order {order.id}: {ve}")

            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            result.update({
                "errors": [str(ve)],
                "suggested_discounts": suggestions,
            })
            return result

        except Exception as e:
            logger.exception(f"Critical error applying discounts on order {order.id}: {e}")
            notify_admin_of_error(f"Discount error on order {order.id}: {e}")

            suggestions = DiscountSuggestionService.get_suggestions(order.website)
            result.update({
                "errors": ["Unexpected internal error. Please try again later."],
                "suggested_discounts": suggestions,
            })
            return result
        
    @staticmethod
    def get_critical_threshold():
        setting = CriticalDeadlineSetting.objects.first()
        return setting.threshold_hours if setting else 24

    @staticmethod
    def update_order_status_based_on_deadline(order):
        if not order.deadline:
            return

        threshold = OrderService.get_critical_threshold()
        now = datetime.utcnow()
        remaining = order.deadline - now

        if remaining <= timedelta(hours=threshold):
            if order.status != OrderStatus.CRITICAL:
                order.status = OrderStatus.CRITICAL
                order.save(update_fields=["status"])
        else:
            if order.status == OrderStatus.CRITICAL:
                # fallback to a sensible default state
                order.status = OrderStatus.PENDING
                order.save(update_fields=["status"])