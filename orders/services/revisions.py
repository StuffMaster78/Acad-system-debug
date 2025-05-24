from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from orders.models import Order
from .utils import get_order_config
from orders.exceptions import PolicyNotFound
from orders.order_enums import OrderStatus

class OrderRevisionService:
    """Handles order revision business logic and state transitions."""

    def __init__(self, order, user):
        self.order = order
        self.user = user

    def get_revision_deadline(self):
        """
        Get the maximum number of days after which revisions are no longer allowed.
        Fetches this configuration from the order settings.

        Args:
            website (Website): The website the order belongs to.

        Returns:
            timedelta: The revision deadline as a timedelta object.
        """
        policy = get_order_config(self.order.website)
        if not policy:
            raise PolicyNotFound("No active revision policy found for this website.")

        return timedelta(days=policy.free_revision_days)


    def is_within_revision_period(self):
        """
        Check if the order is within the allowed revision period.
        Revisions are only allowed if the order was completed within the configured time limit.

        Args:
            order (Order): The order to check.

        Returns:
            bool: True if revision is within the allowed period, False otherwise.
        """
        if not self.order.completed_at:
            return False
        return timezone.now() - self.order.completed_at <= self.get_revision_deadline()


    def can_request_revision(self):
        """
        Check whether the order is eligible for a revision request.
        This checks if the order is in 'Completed'
        state and is within the revision period.

        Args:
            order (Order): The order to check.
            request_user (User): The user making the request.

        Returns:
            bool: True if the revision can be requested, False otherwise.
        """
        if self.order.client != self.user:
            raise PermissionDenied("Only the client can request revisions.")
        return self.is_within_revision_period()


    def request_revision(self, reason):
        """
        Handle the revision request for a given order.

        Args:
            order (Order): The order to revise.
            reason (str): The reason the client is requesting the revision.
            request_user (User): The user making the request.

        Returns:
            bool: True if revision was successfully requested, False otherwise.
        """
        if not self.can_request_revision():
            return False

        self.order.revision_request = reason
        self.order.status = OrderStatus.IN_REVISION.value
        self.order.save(update_fields=["revision_request", "status"])
        return True


    def process_revision(self, revised_work):
        """
        Process the revision of an order by the writer.

        Args:
            order (Order): The order being revised.
            revised_work (str): The revised work content.

        Returns:
            bool: True if the revision was successfully processed, False otherwise.
        """
        if self.order.status != OrderStatus.IN_REVISION.value:
            return False

        self.order.revised_work = revised_work
        self.order.status = OrderStatus.COMPLETED.value
        self.order.save(update_fields=["revised_work", "status"])
        return True


    def deny_revision(self, reason):
        """
        Deny the revision request for an order.

        Args:
            order (Order): The order for which the revision is denied.
            reason (str): The reason for denying the revision.

        Returns:
            bool: True if the revision was denied, False otherwise.
        """
        if self.order.status != OrderStatus.IN_REVISION.value:
            return False

        self.order.revision_request_denied_reason = reason
        self.order.status = OrderStatus.REVISION_DENIED.value
        self.order.save(update_fields=["revision_request_denied_reason", "status"])
        return True