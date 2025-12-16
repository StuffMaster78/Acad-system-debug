from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Order, PreferredWriterResponse
from orders.order_enums import OrderStatus


class PreferredWriterResponseService:
    """Service to handle preferred writer responses on assigned orders.

    This service supports accepting, declining an assigned order, and 
    releasing orders back to the available pool if the acceptance window 
    expires without response.

    Attributes:
        RESPONSE_ACCEPTED (str): Constant for accepted response.
        RESPONSE_DECLINED (str): Constant for declined response.
        ACCEPTANCE_WINDOW_FRACTION (float): Fraction of deadline allowed
            for acceptance before auto-release.
    """

    RESPONSE_ACCEPTED = "accepted"
    RESPONSE_DECLINED = "declined"
    ACCEPTANCE_WINDOW_FRACTION = 0.2

    @staticmethod
    def accept(order_id, writer):
        """Accept an assigned order by the preferred writer.

        Args:
            order_id (int): ID of the order being accepted.
            writer (User): Writer responding to the order.

        Returns:
            Order: The updated order with status 'in_progress'.

        Raises:
            ObjectDoesNotExist: If order does not exist or writer
                is not assigned as preferred.
            ValueError: If order status is not 'pending_preferred'.
        """
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.preferred_writer != writer:
                raise ObjectDoesNotExist(
                    "Order not assigned to this writer."
                )

            if order.status != OrderStatus.PENDING_PREFERRED.value:
                raise ValueError(
                    f"Order is not currently pending preferred writer response. "
                    f"Current status: {order.status}"
                )

            # Check if response already exists
            PreferredWriterResponse.objects.get_or_create(
                order=order,
                defaults={
                    'website': order.website,
                    'writer': writer,
                    'response': PreferredWriterResponseService.RESPONSE_ACCEPTED,
                }
            )

            # Assign writer
            order.assigned_writer = writer
            order.accepted_at = timezone.now()
            order.save()
            
            # Use unified transition helper to move to in_progress
            from orders.services.transition_helper import OrderTransitionHelper
            OrderTransitionHelper.transition_order(
                order,
                OrderStatus.IN_PROGRESS.value,
                user=writer,
                reason="Preferred writer accepted assignment",
                action="preferred_writer_accept",
                is_automatic=False,
                skip_payment_check=True,  # Payment already validated when order was created
                metadata={
                    "preferred_writer_id": writer.id,
                }
            )

            return order

    @staticmethod
    def reject(order_id, writer, reason=None):
        """Reject an assigned order by the preferred writer.

        Args:
            order_id (int): ID of the order being declined.
            writer (User): Writer responding to the order.
            reason (str, optional): Reason for declining.

        Returns:
            Order: The updated order with status 'available'.

        Raises:
            ObjectDoesNotExist: If order does not exist or writer
                is not assigned as preferred.
            ValueError: If order status is not 'pending_preferred'.
        """
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.preferred_writer != writer:
                raise ObjectDoesNotExist(
                    "Order not assigned to this writer."
                )

            if order.status != OrderStatus.PENDING_PREFERRED.value:
                raise ValueError(
                    f"Order is not currently pending preferred writer response. "
                    f"Current status: {order.status}"
                )

            PreferredWriterResponse.objects.get_or_create(
                order=order,
                defaults={
                    'website': order.website,
                    'writer': writer,
                    'response': PreferredWriterResponseService.RESPONSE_DECLINED,
                    'reason': reason,
                }
            )

            # Clear preferred writer
            order.preferred_writer = None
            order.save()
            
            # Use unified transition helper to move to available
            from orders.services.transition_helper import OrderTransitionHelper
            OrderTransitionHelper.transition_order(
                order,
                OrderStatus.AVAILABLE.value,
                user=writer,
                reason=reason or "Preferred writer rejected assignment",
                action="preferred_writer_reject",
                is_automatic=False,
                metadata={
                    "preferred_writer_id": writer.id,
                    "rejection_reason": reason,
                }
            )

            return order

    @staticmethod
    def release_if_expired():
        """Release assigned orders if acceptance window expired.

        Finds orders with status 'pending_preferred' where the preferred writer 
        failed to respond within the acceptance window (20% of time 
        between creation and deadline). Such orders are moved back to 
        'available' and preferred_writer is cleared.

        This method is intended to be called periodically by a background 
        job or scheduler.
        """
        now = timezone.now()
        pending_orders = Order.objects.filter(status=OrderStatus.PENDING_PREFERRED.value)

        for order in pending_orders:
            if not order.created_at or not order.deadline:
                continue

            total_time = order.deadline - order.created_at
            acceptance_window = timedelta(
                seconds=total_time.total_seconds() *
                PreferredWriterResponseService.ACCEPTANCE_WINDOW_FRACTION
            )

            expire_time = order.created_at + acceptance_window
            if now > expire_time:
                with transaction.atomic():
                    locked_order = Order.objects.select_for_update().get(
                        id=order.id
                    )
                    if locked_order.status == OrderStatus.PENDING_PREFERRED.value:
                        # Clear preferred writer
                        locked_order.preferred_writer = None
                        locked_order.save()
                        
                        # Use unified transition helper
                        from orders.services.transition_helper import OrderTransitionHelper
                        try:
                            OrderTransitionHelper.transition_order(
                                locked_order,
                                OrderStatus.AVAILABLE.value,
                                user=None,  # System action
                                reason="Preferred writer acceptance window expired",
                                action="auto_release_preferred",
                                is_automatic=True,
                                metadata={
                                    "preferred_writer_id": order.preferred_writer.id if order.preferred_writer else None,
                                    "expired_at": now.isoformat(),
                                }
                            )
                        except (InvalidTransitionError, AlreadyInTargetStatusError):
                            # Order may have already transitioned, ignore
                            pass