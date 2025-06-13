from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

from order_configs.models import CriticalDeadlineSetting
from orders.exceptions import TransitionNotAllowed
from orders.services.order_utils import _get_order, save_order

logger = logging.getLogger(__name__)

class OrderService:
    """
    Service class handling order lifecycle, state transitions, and discount
    applications. Uses `OrderStatus` enums for status management.
    """

    @staticmethod
    def create_order(user, topic: str, deadline: Optional[str], **kwargs):
        """
        Create a new order and assign initial status based on urgency.
        """
        from orders.services.utils import check_if_urgent
        from orders.models import Order, OrderStatus
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
    def _assert_status(order, allowed_statuses: List[Any]) -> None:
        """
        Helper to assert order's current status is in allowed_statuses.
        """
        from orders.models import OrderStatus
        if OrderStatus(order.status) not in allowed_statuses:
            allowed_names = [status.name for status in allowed_statuses]
            raise TransitionNotAllowed(
                f"Transition not allowed from status '{order.status}'. "
                f"Allowed statuses: {allowed_names}"
            )

    @staticmethod
    @transaction.atomic
    def transition_to_pending(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        allowed = [OrderStatus.UNPAID, OrderStatus.AVAILABLE]
        OrderService._assert_status(order, allowed)
        order.status_enum = OrderStatus.PENDING
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def put_on_hold(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.ON_HOLD
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def resume_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ON_HOLD])
        order.status_enum = OrderStatus.ASSIGNED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def assign_writer(order_id: int, writer):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.PENDING])
        order.status_enum = OrderStatus.ASSIGNED
        order.writer = writer
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def complete_order(order_id: int, completed_by: Optional[Any] = None, completion_notes: Optional[str] = None):
        from orders.models import OrderStatus
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
    def dispute_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        allowed = [OrderStatus.ASSIGNED, OrderStatus.REVISION]
        OrderService._assert_status(order, allowed)
        order.status_enum = OrderStatus.DISPUTED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def approve_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.COMPLETED])
        order.status_enum = OrderStatus.APPROVED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int):
        from orders.models import OrderStatus
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
    def archive_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.COMPLETED])
        order.status_enum = OrderStatus.ARCHIVED
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def late_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.LATE
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def revision_order(order_id: int):
        from orders.models import OrderStatus
        order = _get_order(order_id)
        OrderService._assert_status(order, [OrderStatus.ASSIGNED])
        order.status_enum = OrderStatus.REVISION
        save_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def review_order(order_id: int):
        from orders.models import OrderStatus
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
        """
        from discounts.services.discount_engine import DiscountEngine
        from discounts.services.discount_hints import DiscountHintService
        from discounts.services.discount_suggestions import DiscountSuggestionService
        from discounts.services.discount_usage_tracker import DiscountUsageTracker
        from django.core.exceptions import ValidationError
        from notifications_system.services.send_notification import notify_admin_of_error

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
                "final_price": discount_result.get("final_price", result["final_price"]),
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
        from orders.models import OrderStatus
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
                order.status = OrderStatus.PENDING
                order.save(update_fields=["status"])