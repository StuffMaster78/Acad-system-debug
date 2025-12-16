from django.core.exceptions import ValidationError
from orders.models import Order
from orders.utils.order_utils import get_order_by_id, save_order
from orders.exceptions import InvalidTransitionError, AlreadyInTargetStatusError
from notifications_system.services.notification_helper import NotificationHelper


class MarkOrderPaidService:
    """
    Service to mark an order as paid.

    Methods:
        mark_paid: Transitions the order to 'in_progress' if allowed.
    """

    def mark_paid(self, order_id: int) -> Order:
        """
        Mark an order as paid and move to in_progress.
        Validates that payment has been completed before allowing transition.

        Args:
            order_id (int): ID of the order to mark as paid.

        Returns:
            Order: The updated order instance.

        Raises:
            ValueError: If the order cannot be marked as paid.
            ValidationError: If no completed payment exists.
        """
        order = get_order_by_id(order_id)

        # Validate payment exists
        from django.apps import apps
        OrderPayment = apps.get_model('order_payments_management', 'OrderPayment')
        
        has_completed_payment = OrderPayment.objects.filter(
            order=order,
            status__in=['completed', 'succeeded']
        ).exists()

        if not has_completed_payment:
            raise ValidationError(
                f"Cannot mark order {order_id} as paid: "
                "No completed payment found. Payment must be completed first."
            )

        # Allow transition from 'unpaid' or 'pending'
        if order.status not in ['unpaid', 'pending']:
            raise ValueError(
                f"Order {order_id} cannot be marked paid from status "
                f"{order.status}. Current status must be 'unpaid' or 'pending'."
            )

        order.is_paid = True
        order.save(update_fields=['is_paid'])
        
        # Use unified transition helper to move to in_progress
        # unpaid can now directly transition to in_progress when payment is completed
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            order,
            'in_progress',
            user=None,  # System action
            reason="Order paid and ready for assignment",
            action="mark_paid",
            is_automatic=True,
            skip_payment_check=True,  # We already validated payment
            metadata={
                "payment_validated": True,
                "is_paid": True,
            }
        )
        
        # Send notification
        try:
            # Get payment amount
            from django.apps import apps
            OrderPayment = apps.get_model('order_payments_management', 'OrderPayment')
            payment = OrderPayment.objects.filter(
                order=order,
                status__in=['completed', 'succeeded']
            ).order_by('-created_at').first()
            
            if payment:
                NotificationHelper.notify_order_paid(
                    order=order,
                    payment_amount=payment.discounted_amount or payment.amount,
                    payment_method=payment.payment_method or "payment method"
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send order paid notification: {e}")
        
        return order