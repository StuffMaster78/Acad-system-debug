from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models.orders import Order
from orders.utils.order_utils import get_order_by_id, save_order
from orders.exceptions import InvalidTransitionError, AlreadyInTargetStatusError
from notifications_system.services.notification_service import NotificationService
from payments_processor.models import PaymentIntent
from payments_processor.enums import PaymentIntentPurpose, PaymentIntentStatus, PaymentProvider
from payments_processor.utils.references import generate_payment_reference


class MarkOrderPaidService:
    """
    Service to mark an order as paid.

    Methods:
        mark_paid: Transitions the order to 'in_progress' if allowed.
    """

    def mark_paid(self, order_id: int, reference_id: str = None, payment_method: str = None) -> Order:
        """
        Mark an order as paid and move to in_progress.
        For client payments that were not captured correctly, creates a payment record.

        Args:
            order_id (int): ID of the order to mark as paid.
            reference_id (str, optional): External payment reference (MPESA, PayPal, etc.)
            payment_method (str, optional): Payment method used.

        Returns:
            Order: The updated order instance.
        """
        order = get_order_by_id(order_id)

        from django.contrib.contenttypes.models import ContentType
        order_ct = ContentType.objects.get_for_model(Order)

        has_completed_payment = (
            order.is_paid
            or PaymentIntent.objects.filter(
                payable_content_type=order_ct,
                payable_object_id=order.pk,
                status=PaymentIntentStatus.SUCCEEDED,
            ).exists()
        )

        if not has_completed_payment and reference_id:
            PaymentIntent.objects.create(
                reference=generate_payment_reference(prefix="manual"),
                client=order.client,
                website=order.website,
                purpose=PaymentIntentPurpose.ORDER,
                provider=PaymentProvider.MOCK,
                status=PaymentIntentStatus.SUCCEEDED,
                amount=order.total_price or 0,
                payable=order,
                provider_transaction_id=reference_id,
                paid_at=timezone.now(),
                metadata={"payment_method": payment_method or "manual", "captured_manually": True},
            )
            has_completed_payment = True

        if not has_completed_payment:
            raise ValidationError(
                f"Cannot mark order {order_id} as paid: "
                "No completed payment found. Either provide a reference_id for manual payment "
                "or ensure payment is completed first."
            )

        if order.status not in ['unpaid', 'pending']:
            raise ValueError(
                f"Order {order_id} cannot be marked paid from status "
                f"{order.status}. Current status must be 'unpaid' or 'pending'."
            )

        order.is_paid = True
        order.save(update_fields=['is_paid'])

        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            order,
            'in_progress',
            user=None,
            reason="Order paid and ready for assignment",
            action="mark_paid",
            is_automatic=True,
            skip_payment_check=True,
            metadata={"payment_validated": True, "is_paid": True},
        )

        try:
            NotificationService.notify(
                event_key="order_paid",
                recipient=order.client,
                website=order.website,
                context={
                    "order_id": order.id,
                    "payment_amount": order.total_price,
                    "payment_method": payment_method or "payment method",
                },
                is_critical=True,
                priority="high",
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send order paid notification: {e}")

        return order
