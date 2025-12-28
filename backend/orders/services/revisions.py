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
            raise PolicyNotFound(
                "No active revision policy found for this website."
            )

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
        # If order is not completed, allow revision (for other statuses like submitted, reviewed, etc.)
        if self.order.status != OrderStatus.COMPLETED.value:
            return True
        
        # For completed orders, check if within revision period
        # Get completion time from transition log since Order model doesn't have completed_at
        from orders.models import OrderTransitionLog
        completed_transition = OrderTransitionLog.objects.filter(
            order=self.order,
            new_status=OrderStatus.COMPLETED.value
        ).order_by('-timestamp').first()
        
        if not completed_transition:
            # If no transition log found, check updated_at as fallback
            # This handles edge cases where transition log might be missing
            completed_at = self.order.updated_at
        else:
            completed_at = completed_transition.timestamp
            
        return timezone.now() - completed_at <= self.get_revision_deadline()


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
        # For completed orders, check client permission and revision period
        if self.order.status == OrderStatus.COMPLETED.value:
            user_role = getattr(self.user, 'role', None)
            # Clients must be the order owner, admins can override
            if self.order.client != self.user and user_role not in ['admin', 'superadmin', 'support']:
                raise PermissionDenied("Only the client or admin can request revisions for completed orders.")
            return self.is_within_revision_period()
        else:
            # For non-completed orders, check client permission
            if self.order.client != self.user:
                user_role = getattr(self.user, 'role', None)
                if user_role not in ['admin', 'superadmin', 'support']:
                    raise PermissionDenied("Only the client can request revisions.")
            return True


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

        from orders.services.transition_helper import OrderTransitionHelper
        
        self.order.revision_request = reason
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='revision_requested',
            user=self.user,
            reason=reason,
            action="request_revision",
            is_automatic=False,
            metadata={"revision_request": reason}
        )
        self.order.save(update_fields=["revision_request"])
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
        from orders.services.transition_helper import OrderTransitionHelper
        
        # Check for revision_in_progress status (string value)
        if self.order.status != 'revision_in_progress':
            return False

        self.order.revised_work = revised_work
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='revised',
            user=self.user,
            reason="Revision completed by writer",
            action="process_revision",
            is_automatic=False,
            metadata={"revised_work": revised_work}
        )
        self.order.save(update_fields=["revised_work"])
        return True


    def deny_revision(self, reason: str) -> bool:
        """
        Deny a client's revision request.

        Business rules:
        - Only orders currently in ``revision_requested`` can be denied.
        - We do **not** try to infer or restore a previous terminal state
          (e.g. ``approved`` or ``completed``) here, since that requires
          additional historical context.
        - Instead, we move the order to a safe, reviewable state
          (``on_hold`` when allowed, otherwise ``cancelled``) and persist
          a human‑readable denial reason.

        Args:
            reason: Explanation for denying the revision.

        Returns:
            bool: ``True`` if the revision was denied and a transition was
            performed, ``False`` otherwise.
        """
        from orders.services.transition_helper import OrderTransitionHelper
        from orders.services.status_transition_service import VALID_TRANSITIONS

        if self.order.status != 'revision_requested':
            return False

        self.order.revision_request_denied_reason = reason

        current_status = self.order.status
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])

        # Prefer moving to on_hold so an admin can make a final decision;
        # fall back to cancelled if on_hold is not allowed from this state.
        target_status = 'on_hold' if 'on_hold' in allowed_transitions else 'cancelled'

        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status=target_status,
            user=self.user,
            reason=f"Revision denied: {reason}",
            action="deny_revision",
            is_automatic=False,
            metadata={
                "revision_request_denied_reason": reason,
                "previous_status": current_status,
                "target_status": target_status,
            },
        )
        self.order.save(update_fields=["revision_request_denied_reason"])
        return True