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
            ValueError: If order status is not 'assigned'.
        """
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.preferred_writer != writer:
                raise ObjectDoesNotExist(
                    "Order not assigned to this writer."
                )

            if order.status != OrderStatus.ASSIGNED:
                raise ValueError("Order is not currently assigned.")

            PreferredWriterResponse.objects.create(
                order=order,
                writer=writer,
                response=PreferredWriterResponseService.RESPONSE_ACCEPTED,
            )

            order.status = OrderStatus.IN_PROGRESS
            order.accepted_at = timezone.now()
            order.save()

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
            ValueError: If order status is not 'assigned'.
        """
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            if order.preferred_writer != writer:
                raise ObjectDoesNotExist(
                    "Order not assigned to this writer."
                )

            if order.status != OrderStatus.ASSIGNED:
                raise ValueError("Order is not currently assigned.")

            PreferredWriterResponse.objects.create(
                order=order,
                writer=writer,
                response=PreferredWriterResponseService.RESPONSE_DECLINED,
                reason=reason,
            )

            order.status = OrderStatus.AVAILABLE
            order.preferred_writer = None
            order.save()

            return order

    @staticmethod
    def release_if_expired():
        """Release assigned orders if acceptance window expired.

        Finds orders with status 'assigned' where the preferred writer 
        failed to respond within the acceptance window (20% of time 
        between assignment and deadline). Such orders are moved back to 
        'available' and preferred_writer is cleared.

        This method is intended to be called periodically by a background 
        job or scheduler.
        """
        now = timezone.now()
        assigned_orders = Order.objects.filter(status=OrderStatus.ASSIGNED)

        for order in assigned_orders:
            if not order.assigned_at or not order.deadline:
                continue

            total_time = order.deadline - order.assigned_at
            acceptance_window = timedelta(
                seconds=total_time.total_seconds() *
                PreferredWriterResponseService.ACCEPTANCE_WINDOW_FRACTION
            )

            expire_time = order.assigned_at + acceptance_window
            if now > expire_time:
                with transaction.atomic():
                    locked_order = Order.objects.select_for_update().get(
                        id=order.id
                    )
                    if locked_order.status == OrderStatus.ASSIGNED:
                        locked_order.status = OrderStatus.AVAILABLE
                        locked_order.preferred_writer = None
                        locked_order.save()