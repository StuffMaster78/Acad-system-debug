from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from orders.models import Order
from orders.order_enums import OrderStatus
from notifications_system.services.core import NotificationService
from orders.services.order_access_service import OrderAccessService
from django.core.exceptions import PermissionDenied
from orders.models import WriterReassignmentLog

User = get_user_model()

class OrderAssignmentService:
    """
    Service to handle assignment and unassignment of writers to orders.
    """

    def __init__(self, order: Order):
        """
        Initializes the OrderAssignmentService.

        Args:
            order (Order): The order to operate on.
        """
        self.order = order

    @transaction.atomic
    def assign_writer(self, writer_id: int, reason, writer_payment_amount=None) -> Order:
        """
        Assigns a writer to an order and updates its status.

        Args:
            writer_id (int): The ID of the writer to assign.
            reason: Reason for assignment/reassignment.
            writer_payment_amount (Decimal, optional): Payment amount set by admin for this writer.
                                                     If not provided, will use level-based calculation.

        Returns:
            Order: The updated order with an assigned writer.
        """
        # Check if actor is admin or support (can override constraints and reassign)
        is_admin_or_support = False
        if hasattr(self, 'actor'):
            actor = self.actor
            # Check if user is staff (Django admin) or has admin/support role
            is_admin_or_support = (
                getattr(actor, 'is_staff', False) or 
                getattr(actor, 'role', None) in ['admin', 'superadmin', 'support']
            )
        
        # Check if order is already assigned
        old_writer = self.order.assigned_writer
        
        # Allow reassignment if actor is admin/support (they can override and reassign)
        if old_writer and not is_admin_or_support:
            raise ValidationError(
                "Order is already assigned to a writer. Only admins/support can reassign orders."
            )

        try:
            writer = User.objects.get(
                id=writer_id,
                role="writer",
                is_active=True
            )
        except User.DoesNotExist:
            raise ObjectDoesNotExist(
                f"Writer with ID {writer_id} does not exist or is not active."
            )

        can_assign = OrderAccessService.can_be_assigned(
            writer=writer,
            order=self.order,
            by_admin=is_admin_or_support
        )

        if not can_assign:
            raise PermissionDenied(
                "Writer level too low for this order."
            )
        
        # Check workload limits (max orders) - admins and support can override
        is_admin_override = is_admin_or_support
        
        if not is_admin_override:
            # Only check workload limits if not admin override
            try:
                writer_profile = writer.writer_profile
                writer_level = writer_profile.writer_level
                
                if writer_level:
                    max_allowed_orders = writer_level.max_orders
                    
                    # Count active assignments (in_progress, on_hold, revision_requested, under_editing)
                    active_assignments = Order.objects.filter(
                        assigned_writer=writer,
                        status__in=[
                            OrderStatus.IN_PROGRESS.value,
                            OrderStatus.ON_HOLD.value,
                            OrderStatus.REVISION_REQUESTED.value,
                            OrderStatus.UNDER_EDITING.value,
                        ]
                    ).count()
                    
                    if active_assignments >= max_allowed_orders:
                        raise ValidationError(
                            f"Writer has reached their maximum order limit ({max_allowed_orders} active orders). "
                            "Admin can override this restriction when assigning manually."
                        )
            except AttributeError:
                # Writer profile or level not found - allow assignment if admin, otherwise warn
                if not is_admin_override:
                    raise ValidationError(
                        "Writer profile or level not found. Admin can override this restriction."
                    )
        
        # Determine if this is a reassignment
        is_reassignment = bool(old_writer and old_writer != writer)
        
        # If reassigning, handle the old assignment acceptance record
        if is_reassignment:
            from orders.models import WriterAssignmentAcceptance
            # Mark any pending acceptance as rejected (if exists)
            try:
                old_acceptance = WriterAssignmentAcceptance.objects.get(
                    order=self.order,
                    status='pending'
                )
                old_acceptance.status = 'rejected'
                old_acceptance.reason = f"Reassigned to another writer: {reason}"
                old_acceptance.responded_at = timezone.now()
                old_acceptance.save()
            except WriterAssignmentAcceptance.DoesNotExist:
                pass  # No pending acceptance to update

        self.order.assigned_writer = writer
        
        # Set writer payment amount if provided by admin
        if writer_payment_amount is not None:
            self.order.writer_compensation = writer_payment_amount
        
        self.order.save()
        
        # Determine target status based on current status
        # If order is already in_progress or other active states, use 'reassigned'
        # Otherwise, use 'pending_writer_assignment' to allow writer acceptance
        from orders.services.status_transition_service import VALID_TRANSITIONS
        
        current_status = self.order.status
        target_status = "pending_writer_assignment"
        
        # If this is a reassignment from an active work state, use 'reassigned'
        if is_reassignment or current_status in ['in_progress', 'submitted', 'under_editing', 'revision_in_progress']:
            # Check if 'reassigned' is a valid transition from current status
            if 'reassigned' in VALID_TRANSITIONS.get(current_status, []):
                target_status = "reassigned"
            # If 'reassigned' is not valid, check if we can go to 'pending_writer_assignment'
            elif 'pending_writer_assignment' not in VALID_TRANSITIONS.get(current_status, []):
                # If neither is valid, try 'available' as fallback
                if 'available' in VALID_TRANSITIONS.get(current_status, []):
                    target_status = "available"
                else:
                    # Last resort: try to go to a state that allows assignment
                    # This shouldn't happen, but handle gracefully
                    raise ValidationError(
                        f"Cannot reassign writer. Order in status '{current_status}' "
                        f"does not allow reassignment. Please put order on hold first."
                    )
        
        # Use unified transition helper
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            self.order,
            target_status,
            user=self.actor if hasattr(self, 'actor') else None,
            reason=reason,
            action="assign_writer",
            is_automatic=False,
            skip_payment_check=is_admin_or_support,  # Admins can override payment check
            metadata={
                "writer_id": writer.id,
                "writer_payment_amount": str(writer_payment_amount) if writer_payment_amount else None,
                "is_reassignment": is_reassignment,
            }
        )
        
        # Create or update assignment acceptance record
        # Only create acceptance record if we're going to pending_writer_assignment
        # For reassigned orders, we still create the record so writer can accept
        from orders.models import WriterAssignmentAcceptance
        
        # If reassigning, mark old acceptance as rejected
        if is_reassignment:
            try:
                old_acceptance = WriterAssignmentAcceptance.objects.get(
                    order=self.order,
                    status='pending'
                )
                old_acceptance.status = 'rejected'
                old_acceptance.reason = f"Reassigned to another writer: {reason}"
                old_acceptance.responded_at = timezone.now()
                old_acceptance.save()
            except WriterAssignmentAcceptance.DoesNotExist:
                pass  # No pending acceptance to update
        
        # Create or update assignment acceptance record
        acceptance, created = WriterAssignmentAcceptance.objects.get_or_create(
            order=self.order,
            defaults={
                'website': self.order.website,
                'writer': writer,
                'assigned_by': self.actor if hasattr(self, 'actor') else None,
                'status': 'pending',
                'reason': reason
            }
        )
        
        # If it already existed (reassignment), update it
        if not created:
            acceptance.writer = writer
            acceptance.assigned_by = self.actor if hasattr(self, 'actor') else None
            acceptance.status = 'pending'
            acceptance.reason = reason
            acceptance.assigned_at = timezone.now()
            acceptance.responded_at = None
            acceptance.save()

        # Send appropriate notifications
        if is_reassignment:
            WriterReassignmentLog.objects.create(
                order=self.order,
                previous_writer=old_writer,
                new_writer=writer,
                reassigned_by=self.actor if hasattr(self, 'actor') else None,
                reason=reason
            )
            self._notify_reassignment(old_writer, writer, reason)
        else:
            self._notify_assignment(writer)

        return self.order


    @transaction.atomic
    def unassign_writer(self) -> Order:
        """
        Unassigns the current writer from an order and sets it back to available.

        Args:
            order (Order): The order to update.

        Returns:
            Order: The updated order with no assigned writer.
        """
        if not self.order.assigned_writer:
            raise ValidationError("Order is not currently assigned to any writer.")

        writer = self.order.assigned_writer
        self.order.assigned_writer = None
        self.order.save()
        
        # Use unified transition helper to move to available
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            self.order,
            "available",
            user=self.actor if hasattr(self, 'actor') else None,
            reason="Writer unassigned",
            action="unassign_writer",
            is_automatic=False,
            metadata={
                "writer_id": writer.id,
            }
        )

        NotificationService.send_notification(
            user=writer,
            event="Order Unassigned",
            context={"order_id": self.order.id}
        )
        NotificationService.send_notification(
            user=self.order.client,
            event="Writer Unassigned",
            context={"order_id": self.order.id},
            message=f"The writer was unassigned from your Order #{self.order.id} and it's now available again."
        )

        return self.order
    

    def _notify_assignment(self, writer):
        NotificationService.send_notification(
            user=writer,
            event="New Order Assigned",
            payload={
                "order_id": self.order.id,
                "message": "You have been assigned a new order. Please accept or reject the assignment.",
                "order_topic": self.order.topic
            },
            website=self.order.website
        )

        NotificationService.send_notification(
            user=self.order.client,
            event="Writer Assigned",
            payload={
                "order_id": self.order.id,
                "message": f"A writer has been assigned to your order. Waiting for writer confirmation."
            },
            website=self.order.website
        )

    def _notify_reassignment(self, old_writer, new_writer, reason):
        NotificationService.send_notification(
            user=old_writer,
            event="Order Reassigned",
            payload={
                "order_id": self.order.id,
                "message": f"Order #{self.order.id} has been reassigned to another writer.",
                "reason": reason
            },
            website=self.order.website
        )

        NotificationService.send_notification(
            user=new_writer,
            event="New Order Assigned",
            payload={
                "order_id": self.order.id,
                "message": "You have been assigned a new order. Please accept or reject the assignment.",
                "order_topic": self.order.topic
            },
            website=self.order.website
        )

        NotificationService.send_notification(
            user=self.order.client,
            event="Writer Reassigned",
            payload={
                "order_id": self.order.id,
                "message": f"Order #{self.order.id} has been reassigned to a new writer. Waiting for writer confirmation."
            },
            website=self.order.website
        )