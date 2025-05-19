from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from orders.models import Order
from .utils import get_order_config
from orders.exceptions import PolicyNotFound

class OrderRevisionService:
    """Handles order revision business logic and state transitions."""

    def __init__(self, order, user):
        self.order = order
        self.user = user

    def get_revision_deadline(website):
        """
        Get the maximum number of days after which revisions are no longer allowed.
        Fetches this configuration from the order settings.

        Args:
            website (Website): The website the order belongs to.

        Returns:
            timedelta: The revision deadline as a timedelta object.
        """
        policy = get_order_config(website)
        if not policy:
            raise PolicyNotFound("No active revision policy found for this website.")

        return timedelta(days=policy.free_revision_days)


    def is_within_revision_period(order):
        """
        Check if the order is within the allowed revision period.
        Revisions are only allowed if the order was completed within the configured time limit.

        Args:
            order (Order): The order to check.

        Returns:
            bool: True if revision is within the allowed period, False otherwise.
        """
        revision_deadline = OrderRevisionService.get_revision_deadline(order.website)
        time_elapsed = timezone.now() - order.completed_at
        return time_elapsed <= revision_deadline


    def can_request_revision(order, request_user):
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
        if order.client != request_user:
            raise PermissionDenied("Only the client can request revisions.")

        policy = order.website.revision_policies.filter(active=True).first()
        if not policy:
            raise PolicyNotFound("No active revision policy found for this website.")

        # Check if the revision request is within the free revision window
        if (timezone.now() - order.created_at).days <= policy.free_revision_days:
            return True

        # Handle post-free revision (maybe with a payment wall)
        return False


    def request_revision(order, reason, request_user):
        """
        Handle the revision request for a given order.

        Args:
            order (Order): The order to revise.
            reason (str): The reason the client is requesting the revision.
            request_user (User): The user making the request.

        Returns:
            bool: True if revision was successfully requested, False otherwise.
        """
        if not OrderRevisionService.can_request_revision(order, request_user):
            return False

        order.revision_request = reason
        order.status = 'in_revision'
        order.save()

        return True


    def process_revision(order, revised_work):
        """
        Process the revision of an order by the writer.

        Args:
            order (Order): The order being revised.
            revised_work (str): The revised work content.

        Returns:
            bool: True if the revision was successfully processed, False otherwise.
        """
        if order.status != 'in_revision':
            return False

        order.revised_work = revised_work
        order.status = 'completed'
        order.save()

        return True


    def deny_revision(order, reason):
        """
        Deny the revision request for an order.

        Args:
            order (Order): The order for which the revision is denied.
            reason (str): The reason for denying the revision.

        Returns:
            bool: True if the revision was denied, False otherwise.
        """
        if order.status != 'completed':
            return False

        order.revision_request_denied_reason = reason
        order.status = 'revision_denied'
        order.save()

        return True