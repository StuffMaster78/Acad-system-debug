"""
Unified helper for order status transitions.
This module provides a centralized way to handle all order status transitions
with consistent validation, logging, and notifications.
"""
from typing import Optional, Dict, Any, List, Callable
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

from orders.models import Order, OrderTransitionLog
from orders.services.status_transition_service import StatusTransitionService, VALID_TRANSITIONS
from orders.exceptions import InvalidTransitionError, AlreadyInTargetStatusError
from audit_logging.services.audit_log_service import AuditLogService

logger = logging.getLogger(__name__)


# Custom validation rules for specific transitions
# Format: (from_status, to_status): [list of validation functions]
TRANSITION_VALIDATION_RULES: Dict[tuple, List[Callable]] = {
    # Can't cancel paid orders (unless admin override)
    ('paid', 'cancelled'): [
        lambda order, user, **kwargs: _validate_can_cancel_paid_order(order, user, **kwargs)
    ],
    ('in_progress', 'cancelled'): [
        lambda order, user, **kwargs: _validate_can_cancel_paid_order(order, user, **kwargs)
    ],
    ('submitted', 'cancelled'): [
        lambda order, user, **kwargs: _validate_can_cancel_paid_order(order, user, **kwargs)
    ],
    
    # Can't submit without files (optional - can be enabled)
    # ('in_progress', 'submitted'): [
    #     lambda order, user, **kwargs: _validate_has_files(order, **kwargs)
    # ],
    
    # Can't complete without payment
    ('unpaid', 'completed'): [
        lambda order, user, **kwargs: _validate_payment_required(order, **kwargs)
    ],
    
    # Can't archive non-approved orders
    ('approved', 'archived'): [
        lambda order, user, **kwargs: _validate_is_approved(order, **kwargs)
    ],
    
    # Can't rate non-reviewed orders (already handled by status check, but explicit)
    ('reviewed', 'rated'): [
        lambda order, user, **kwargs: _validate_is_reviewed(order, **kwargs)
    ],
}


def _event_for_transition(from_status: str, to_status: str) -> Optional[str]:
    if from_status == "on_hold" and to_status in {"in_progress", "available", "reassigned"}:
        return "order.off_hold"
    mapping = {
        "pending_writer_assignment": "order.assigned",
        "pending_preferred": "order.preferred_writer_assigned",
        "available": "order.available",
        "in_progress": "order.in_progress",
        "on_hold": "order.on_hold",
        "under_editing": "order.under_editing",
        "submitted": "order.submitted",
        "reviewed": "order.reviewed",
        "rated": "order.rated",
        "approved": "order.approved",
        "completed": "order.completed",
        "revision_requested": "order.revision_requested",
        "revision_in_progress": "order.revision_in_progress",
        "revised": "order.revised",
        "reassigned": "order.reassigned",
        "disputed": "order.disputed",
        "cancelled": "order.cancelled",
        "refunded": "order.refunded",
        "archived": "order.archived",
        "unarchived": "order.unarchived",
        "restored": "order.restored",
        "closed": "order.closed",
        "unpaid": "order.unpaid",
        "paid": "order.paid",
    }
    return mapping.get(to_status)


def _emit_transition_notification(
    *,
    order: Order,
    from_status: str,
    to_status: str,
    user=None,
    metadata: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    action: str = "status_transition",
) -> None:
    event_key = _event_for_transition(from_status, to_status)
    if not event_key:
        return
    try:
        from orders.notification_emitters import emit_event
        emit_event(
            event_key,
            order=order,
            actor=user,
            extra={
                "from_status": from_status,
                "to_status": to_status,
                "action": action,
                "reason": reason,
                **(metadata or {}),
            },
        )
    except Exception as exc:
        logger.warning(
            "Failed to emit notification for %s -> %s on order %s: %s",
            from_status, to_status, order.id, exc
        )


def _validate_can_cancel_paid_order(order: Order, user=None, **kwargs) -> None:
    """Validate that paid orders can only be cancelled by admins."""
    skip_payment_check = kwargs.get('skip_payment_check', False)
    
    if order.is_paid and not skip_payment_check:
        # Check if user is admin/support
        is_admin = user and (
            getattr(user, 'is_staff', False) or 
            getattr(user, 'role', None) in ['admin', 'superadmin', 'support']
        )
        if not is_admin:
            raise ValidationError(
                "Cannot cancel a paid order. Only administrators can cancel paid orders. "
                "Please contact support for assistance."
            )


def _validate_payment_required(order: Order, **kwargs) -> None:
    """Validate that order is paid before completing."""
    skip_payment_check = kwargs.get('skip_payment_check', False)
    
    if not skip_payment_check and not order.is_paid:
        raise ValidationError(
            "Order must be paid before it can be completed."
        )


def _validate_is_approved(order: Order, **kwargs) -> None:
    """Validate that order is approved before archiving."""
    if order.status != 'approved':
        raise ValidationError(
            f"Order must be in 'approved' status to be archived. Current status: {order.status}"
        )


def _validate_is_reviewed(order: Order, **kwargs) -> None:
    """Validate that order is reviewed before rating."""
    if order.status != 'reviewed':
        raise ValidationError(
            f"Order must be in 'reviewed' status to be rated. Current status: {order.status}"
        )


def _validate_has_files(order: Order, **kwargs) -> None:
    """Validate that order has files before submission (optional rule)."""
    from order_files.models import OrderFile
    has_files = OrderFile.objects.filter(order=order).exists()
    if not has_files:
        raise ValidationError(
            "Order must have at least one file uploaded before it can be submitted."
        )


# Transition hooks registry
# Format: (from_status, to_status): [list of hook functions]
_BEFORE_TRANSITION_HOOKS: Dict[tuple, List[Callable]] = {}
_AFTER_TRANSITION_HOOKS: Dict[tuple, List[Callable]] = {}


class OrderTransitionHelper:
    """
    Unified helper for order status transitions.
    Provides a single point of entry for all status changes with:
    - Validation
    - Logging (OrderTransitionLog + AuditLog)
    - Notifications (optional)
    - Business rule enforcement
    - Before/After hooks
    """
    
    @staticmethod
    def register_before_hook(
        from_status: str,
        to_status: str,
        callback: Callable[[Order, Optional[Any], Dict[str, Any]], None]
    ) -> None:
        """
        Register a hook to run before a specific transition.
        
        Args:
            from_status: Source status
            to_status: Target status
            callback: Function(order, user, metadata) -> None
        """
        key = (from_status, to_status)
        if key not in _BEFORE_TRANSITION_HOOKS:
            _BEFORE_TRANSITION_HOOKS[key] = []
        _BEFORE_TRANSITION_HOOKS[key].append(callback)
        logger.debug(f"Registered before hook for {from_status} -> {to_status}")
    
    @staticmethod
    def register_after_hook(
        from_status: str,
        to_status: str,
        callback: Callable[[Order, Optional[Any], Dict[str, Any]], None]
    ) -> None:
        """
        Register a hook to run after a specific transition.
        
        Args:
            from_status: Source status
            to_status: Target status
            callback: Function(order, user, metadata) -> None
        """
        key = (from_status, to_status)
        if key not in _AFTER_TRANSITION_HOOKS:
            _AFTER_TRANSITION_HOOKS[key] = []
        _AFTER_TRANSITION_HOOKS[key].append(callback)
        logger.debug(f"Registered after hook for {from_status} -> {to_status}")
    
    @staticmethod
    def _run_before_hooks(
        order: Order,
        from_status: str,
        to_status: str,
        user=None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Run all before hooks for this transition."""
        key = (from_status, to_status)
        hooks = _BEFORE_TRANSITION_HOOKS.get(key, [])
        
        for hook in hooks:
            try:
                hook(order, user, metadata or {})
            except Exception as e:
                logger.error(
                    f"Before hook failed for {from_status} -> {to_status} on order #{order.id}: {e}",
                    exc_info=True
                )
                # Don't fail the transition if hook fails, but log it
                # Could optionally raise if hooks are critical
    
    @staticmethod
    def _run_after_hooks(
        order: Order,
        from_status: str,
        to_status: str,
        user=None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Run all after hooks for this transition."""
        key = (from_status, to_status)
        hooks = _AFTER_TRANSITION_HOOKS.get(key, [])
        
        for hook in hooks:
            try:
                hook(order, user, metadata or {})
            except Exception as e:
                logger.error(
                    f"After hook failed for {from_status} -> {to_status} on order #{order.id}: {e}",
                    exc_info=True
                )
                # Don't fail the transition if hook fails, but log it
    
    @staticmethod
    @transaction.atomic
    def transition_order(
        order: Order,
        target_status: str,
        *,
        user=None,
        reason: Optional[str] = None,
        action: str = "status_transition",
        is_automatic: bool = False,
        skip_payment_check: bool = False,
        skip_writer_check: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        log_transition: bool = True,
        log_audit: bool = True,
    ) -> Order:
        """
        Transition an order to a new status with full validation and logging.
        
        Args:
            order: The order instance to transition
            target_status: Target status (string value)
            user: User performing the transition (for logging)
            reason: Optional reason for the transition
            action: Action name for logging (e.g., "assign_writer", "accept_assignment")
            is_automatic: Whether this is an automatic transition
            skip_payment_check: Skip payment validation (admin override)
            skip_writer_check: Skip writer assignment validation (admin override)
            metadata: Additional metadata for logging
            log_transition: Whether to log to OrderTransitionLog
            log_audit: Whether to log to AuditLog
            
        Returns:
            Order: The updated order instance
            
        Raises:
            AlreadyInTargetStatusError: If order is already in target status
            InvalidTransitionError: If transition is not allowed
            ValidationError: If business rules are violated
        """
        current_status = order.status
        
        # Check if already in target status
        if target_status == current_status:
            raise AlreadyInTargetStatusError(
                f"Order #{order.id} is already in status '{target_status}'."
            )
        
        # Validate transition is allowed
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
        if target_status not in allowed_transitions:
            raise InvalidTransitionError(
                f"Cannot transition Order #{order.id} from '{current_status}' to '{target_status}'. "
                f"Allowed transitions: {', '.join(allowed_transitions)}"
            )
        
        # Run custom validation rules for this specific transition
        transition_key = (current_status, target_status)
        if transition_key in TRANSITION_VALIDATION_RULES:
            validation_functions = TRANSITION_VALIDATION_RULES[transition_key]
            for validate_func in validation_functions:
                try:
                    validate_func(
                        order=order,
                        user=user,
                        skip_payment_check=skip_payment_check,
                        skip_writer_check=skip_writer_check,
                        metadata=metadata
                    )
                except ValidationError:
                    raise  # Re-raise validation errors as-is
                except Exception as e:
                    raise ValidationError(f"Validation failed: {str(e)}")
        
        # Run before hooks
        OrderTransitionHelper._run_before_hooks(
            order=order,
            from_status=current_status,
            to_status=target_status,
            user=user,
            metadata=metadata
        )
        
        # Use StatusTransitionService for validation and business rules
        transition_service = StatusTransitionService(user=user)
        
        # Build metadata
        transition_metadata = {
            "action": action,
            "is_automatic": is_automatic,
            **(metadata or {})
        }
        
        # Perform transition with validation (StatusTransitionService will log to OrderTransitionLog)
        # We disable its audit log and handle it ourselves to avoid duplicates
        try:
            updated_order = transition_service.transition_order_to_status(
                order,
                target_status,
                metadata=transition_metadata,
                log_action=log_audit,  # Let StatusTransitionService handle audit log
                skip_payment_check=skip_payment_check,
                reason=reason
            )
        except ValidationError as e:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ValidationError(f"Transition failed: {str(e)}")
        
        # Run after hooks
        OrderTransitionHelper._run_after_hooks(
            order=updated_order,
            from_status=current_status,
            to_status=target_status,
            user=user,
            metadata=metadata
        )

        _emit_transition_notification(
            order=updated_order,
            from_status=current_status,
            to_status=target_status,
            user=user,
            metadata=metadata,
            reason=reason,
            action=action,
        )
        
        return updated_order
    
    @staticmethod
    def can_transition(order: Order, target_status: str) -> bool:
        """
        Check if an order can transition to a target status.
        
        Args:
            order: The order instance
            target_status: Target status to check
            
        Returns:
            bool: True if transition is allowed
        """
        current_status = order.status
        if current_status == target_status:
            return False
        
        allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
        return target_status in allowed_transitions
    
    @staticmethod
    def get_available_transitions(order: Order) -> list[str]:
        """
        Get list of available transitions for an order.
        
        Args:
            order: The order instance
            
        Returns:
            List of available target statuses
        """
        current_status = order.status
        return VALID_TRANSITIONS.get(current_status, [])

