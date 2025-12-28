from decimal import Decimal

from django.apps import apps
from django.db import transaction
from orders.order_enums import OrderStatus
from orders.utils.order_utils import get_order_by_id, save_order


class CancelOrderService:
    """
    Service for canceling an order.

    Methods:
        cancel_order: Cancels an order if allowed (for admins).
        request_cancellation: Creates a cancellation request (for clients).
    """

    @staticmethod
    @transaction.atomic
    def cancel_order(order_id: int, reason: str = "", user=None) -> None:
        """
        Cancels the order directly (admin-only action).
        
        For clients, use request_cancellation() instead.

        Args:
            order_id (int): The ID of the order to cancel.
            reason (str): Optional reason for cancellation.
            user (User, optional): User requesting cancellation (must be admin/superadmin/support).

        Raises:
            ValueError: If the order cannot be canceled or user is not authorized.
        """
        order = get_order_by_id(order_id)

        # Only admins can directly cancel
        if user and not (user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']):
            raise ValueError(
                "Clients cannot directly cancel orders. Please use request_cancellation() instead."
            )

        # Check if order can be cancelled (convert enum values to strings for comparison)
        non_cancellable_statuses = [
            OrderStatus.CANCELLED.value,
            OrderStatus.COMPLETED.value,
            OrderStatus.RATED.value,
            OrderStatus.REVIEWED.value,
            OrderStatus.APPROVED.value,
            OrderStatus.ARCHIVED.value,
            OrderStatus.UNPAID.value,
            OrderStatus.PENDING.value,
            OrderStatus.REJECTED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.REFUNDED.value,
        ]
        
        if order.status in non_cancellable_statuses:
            raise ValueError(
                f"Cannot cancel order in status '{order.status}'."
            )

        # Optional: Save reason or audit log
        if hasattr(order, "cancellation_reason"):
            order.cancellation_reason = reason
            order.save(update_fields=["cancellation_reason"])

        # Use unified transition helper to move to cancelled
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            order,
            OrderStatus.CANCELLED.value,
            user=user,  # Pass user for audit logging
            reason=reason or "Order cancelled",
            action="cancel_order",
            is_automatic=False,
            metadata={
                "cancellation_reason": reason,
                "cancelled_by_admin": True,
            }
        )
    
    @staticmethod
    @transaction.atomic
    def request_cancellation(order_id: int, reason: str, user, threshold_percentage: Decimal = None) -> 'CancellationRequest':
        """
        Create a cancellation request for a client.
        
        Calculates forfeiture based on deadline percentage:
        - Below threshold (default 50%): No forfeiture, full refund
        - Above threshold: Progressive forfeiture (up to 80% max)
        
        Args:
            order_id (int): The ID of the order to request cancellation for.
            reason (str): Client's reason for requesting cancellation.
            user (User): Client requesting cancellation.
            threshold_percentage (Decimal, optional): Deadline percentage threshold (default 50%).
        
        Returns:
            CancellationRequest: The created cancellation request.
        
        Raises:
            ValueError: If the order cannot have a cancellation requested.
        """
        from orders.models import CancellationRequest
        
        if threshold_percentage is None:
            threshold_percentage = Decimal('50.00')
        
        order = get_order_by_id(order_id)
        
        # Verify user is the order's client
        if order.client != user:
            raise ValueError("Only the order's client can request cancellation.")
        
        # Check if order can have cancellation requested
        non_cancellable_statuses = [
            OrderStatus.CANCELLED.value,
            OrderStatus.COMPLETED.value,
            OrderStatus.RATED.value,
            OrderStatus.REVIEWED.value,
            OrderStatus.APPROVED.value,
            OrderStatus.ARCHIVED.value,
            OrderStatus.REFUNDED.value,
        ]
        
        if order.status in non_cancellable_statuses:
            raise ValueError(
                f"Cannot request cancellation for order in status '{order.status}'."
            )
        
        # Check if there's already a pending request
        existing_request = CancellationRequest.objects.filter(
            order=order,
            status='pending'
        ).first()
        
        if existing_request:
            raise ValueError(
                "A pending cancellation request already exists for this order."
            )
        
        # Create cancellation request
        cancellation_request = CancellationRequest.objects.create(
            order=order,
            requested_by=user,
            reason=reason,
            status='pending'
        )
        
        # Calculate forfeiture
        cancellation_request.calculate_forfeiture(threshold_percentage)
        
        return cancellation_request