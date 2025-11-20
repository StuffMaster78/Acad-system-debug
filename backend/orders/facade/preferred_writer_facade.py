from django.core.exceptions import ObjectDoesNotExist, ValidationError
from orders.services.preferred_writer_response import (
    PreferredWriterResponseService,
)


class PreferredWriterResponseFacade:
    """Facade to simplify interaction with PreferredWriterResponseService.

    Provides a clean interface to accept, reject, or auto-release orders
    assigned to preferred writers without exposing service details.
    """

    @staticmethod
    def accept_order(order_id, writer):
        """Accept the order on behalf of the preferred writer.

        Args:
            order_id (int): ID of the order to accept.
            writer (User): The writer accepting the order.

        Returns:
            Order: The updated order after acceptance.

        Raises:
            ObjectDoesNotExist: If the order is not found or writer
                is not assigned.
            ValidationError: If order is not in 'assigned' state.
        """
        try:
            return PreferredWriterResponseService.accept(order_id, writer)
        except ObjectDoesNotExist as e:
            # Here you can log or re-raise with a custom message if needed
            raise e
        except ValueError as e:
            raise ValidationError(str(e))

    @staticmethod
    def reject_order(order_id, writer, reason=None):
        """Reject the order on behalf of the preferred writer.

        Args:
            order_id (int): ID of the order to reject.
            writer (User): The writer rejecting the order.
            reason (str, optional): Reason for rejection.

        Returns:
            Order: The updated order after rejection.

        Raises:
            ObjectDoesNotExist: If order is missing or writer not assigned.
            ValidationError: If order is not in 'assigned' state.
        """
        try:
            return PreferredWriterResponseService.reject(order_id, writer, reason)
        except ObjectDoesNotExist as e:
            raise e
        except ValueError as e:
            raise ValidationError(str(e))

    @staticmethod
    def auto_release_expired_orders():
        """Auto-release all assigned orders where acceptance time expired.

        No arguments. Intended for scheduled tasks or cron jobs.
        """
        PreferredWriterResponseService.release_if_expired()