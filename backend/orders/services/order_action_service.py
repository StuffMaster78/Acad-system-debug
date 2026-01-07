"""
Order Action Service - State-aware action system
Determines available actions based on order state and automatically triggers transitions.
"""
from typing import List, Dict, Optional, Set
from django.core.exceptions import ValidationError

from orders.models import Order
from orders.services.status_transition_service import StatusTransitionService, VALID_TRANSITIONS


# Map order status to available actions
STATUS_ACTIONS_MAP: Dict[str, List[Dict[str, any]]] = {
    "pending": [
        {"action": "mark_paid", "label": "Mark as Paid", "target_status": "paid", "roles": ["admin", "superadmin", "support"]},
        {"action": "assign_order", "label": "Assign Writer", "target_status": "pending_writer_assignment", "roles": ["admin", "superadmin", "support"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin", "client"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "unpaid": [
        {"action": "mark_paid", "label": "Mark as Paid", "target_status": "paid", "roles": ["admin", "superadmin", "support", "client"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin", "client"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "paid": [
        {"action": "assign_order", "label": "Assign Writer", "target_status": "available", "roles": ["admin", "superadmin", "support"]},
        {"action": "make_available", "label": "Make Available", "target_status": "available", "roles": ["admin", "superadmin", "support"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "available": [
        {"action": "assign_order", "label": "Assign Writer", "target_status": None, "roles": ["admin", "superadmin", "support", "writer"]},
        {"action": "start_order", "label": "Start Order", "target_status": "in_progress", "roles": ["writer"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "in_progress": [
        {"action": "submit_order", "label": "Submit Order", "target_status": "submitted", "roles": ["writer"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["writer", "admin", "superadmin", "support"]},
        {"action": "reassign_order", "label": "Reassign Order", "target_status": "reassigned", "roles": ["admin", "superadmin", "support"]},
        {"action": "move_to_editing", "label": "Move to Editing", "target_status": "under_editing", "roles": ["admin", "superadmin", "editor"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "submitted": [
        {"action": "review_order", "label": "Review Order", "target_status": "reviewed", "roles": ["admin", "superadmin", "support", "editor"]},
        {"action": "rate_order", "label": "Rate Order", "target_status": "rated", "roles": ["admin", "superadmin"]},
        {"action": "request_revision", "label": "Request Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin", "client", "support"]},
        {"action": "move_to_editing", "label": "Move to Editing", "target_status": "under_editing", "roles": ["admin", "superadmin", "editor"]},
        {"action": "dispute_order", "label": "Dispute Order", "target_status": "disputed", "roles": ["client", "admin", "superadmin"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "under_editing": [
        {"action": "submit_order", "label": "Submit After Editing", "target_status": "submitted", "roles": ["editor", "admin", "superadmin"]},
        {"action": "return_to_writer", "label": "Return to Writer", "target_status": "in_progress", "roles": ["editor", "admin", "superadmin"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "reviewed": [
        {"action": "rate_order", "label": "Rate Order", "target_status": "rated", "roles": ["admin", "superadmin"]},
        {"action": "request_revision", "label": "Request Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin", "client"]},
        {"action": "approve_order", "label": "Approve Order", "target_status": "approved", "roles": ["admin", "superadmin"]},
    ],
    "rated": [
        {"action": "approve_order", "label": "Approve Order", "target_status": "approved", "roles": ["admin", "superadmin"]},
        {"action": "complete_order", "label": "Complete Order", "target_status": "completed", "roles": ["admin", "superadmin"]},
        {"action": "request_revision", "label": "Request Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin", "client"]},
    ],
    "approved": [
        {"action": "complete_order", "label": "Complete Order", "target_status": "completed", "roles": ["admin", "superadmin"]},
        {"action": "archive_order", "label": "Archive Order", "target_status": "archived", "roles": ["admin", "superadmin"]},
    ],
    "completed": [
        {"action": "approve_order", "label": "Approve Order", "target_status": "approved", "roles": ["admin", "superadmin"]},
        {"action": "archive_order", "label": "Archive Order", "target_status": "archived", "roles": ["admin", "superadmin"]},
        {"action": "close_order", "label": "Close Order", "target_status": "closed", "roles": ["admin", "superadmin"]},
        {"action": "request_revision", "label": "Request Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin", "client", "support"]},
        # Note: reassign_order is NOT available for completed orders
        # Note: edit_order is available for completed orders (for admin corrections)
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "revision_requested": [
        {"action": "start_revision", "label": "Start Revision", "target_status": "revision_in_progress", "roles": ["writer", "admin", "superadmin"]},
        {"action": "reassign_order", "label": "Reassign Order", "target_status": "reassigned", "roles": ["admin", "superadmin", "support"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "revision_in_progress": [
        {"action": "submit_revision", "label": "Submit Revision", "target_status": "revised", "roles": ["writer"]},
        {"action": "submit_order", "label": "Submit Order", "target_status": "submitted", "roles": ["writer"]},
        {"action": "reassign_order", "label": "Reassign Order", "target_status": "reassigned", "roles": ["admin", "superadmin", "support"]},
        {"action": "hold_order", "label": "Put on Hold", "target_status": "on_hold", "roles": ["admin", "superadmin", "support"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "revised": [
        {"action": "review_order", "label": "Review Revision", "target_status": "reviewed", "roles": ["admin", "superadmin", "support", "editor"]},
        {"action": "rate_order", "label": "Rate Order", "target_status": "rated", "roles": ["admin", "superadmin"]},
        {"action": "approve_order", "label": "Approve Order", "target_status": "approved", "roles": ["admin", "superadmin"]},
        {"action": "request_revision", "label": "Request Another Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin", "client"]},
        {"action": "move_to_editing", "label": "Move to Editing", "target_status": "under_editing", "roles": ["admin", "superadmin", "editor"]},
        {"action": "close_order", "label": "Close Order", "target_status": "closed", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "on_hold": [
        {"action": "resume_order", "label": "Resume Order", "target_status": None, "roles": ["admin", "superadmin", "support", "writer"]},
        {"action": "cancel_order", "label": "Cancel Order", "target_status": "cancelled", "roles": ["admin", "superadmin"]},
        {"action": "edit_order", "label": "Edit Order Details", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "update_order", "label": "Update Order", "target_status": None, "roles": ["admin", "superadmin", "support"]},
    ],
    "reassigned": [
        {"action": "start_order", "label": "Start Order", "target_status": "in_progress", "roles": ["writer"]},
    ],
    "disputed": [
        {"action": "resolve_dispute", "label": "Resolve Dispute", "target_status": None, "roles": ["admin", "superadmin", "support"]},
        {"action": "request_revision", "label": "Request Revision", "target_status": "revision_requested", "roles": ["admin", "superadmin"]},
        {"action": "refund_order", "label": "Refund Order", "target_status": "refunded", "roles": ["admin", "superadmin"]},
    ],
    "cancelled": [
        {"action": "reopen_order", "label": "Reopen Order", "target_status": "reopened", "roles": ["admin", "superadmin"]},
        {"action": "refund_order", "label": "Refund Order", "target_status": "refunded", "roles": ["admin", "superadmin"]},
    ],
    "archived": [
        {"action": "close_order", "label": "Close Order", "target_status": "closed", "roles": ["admin", "superadmin"]},
    ],
    "closed": [],
    "refunded": [
        {"action": "close_order", "label": "Close Order", "target_status": "closed", "roles": ["admin", "superadmin"]},
    ],
}


class OrderActionService:
    """
    Service for managing order actions with automatic status transitions.
    """
    
    def __init__(self, user=None):
        self.user = user
        self.user_role = getattr(user, 'role', None) if user else None
    
    def get_available_actions(self, order: Order) -> List[Dict]:
        """
        Get list of available actions for an order based on its current state.
        Includes business logic validation to ensure actions are appropriate.
        
        Args:
            order: The order instance
            
        Returns:
            List of available action dictionaries with action name, label, and metadata
        """
        current_status = order.status
        # Normalize status - handle both "complete" and "completed"
        if current_status == "complete":
            current_status = "completed"
        all_actions = STATUS_ACTIONS_MAP.get(current_status, [])
        
        # Filter by user role
        if self.user_role:
            available = [
                action for action in all_actions
                if self.user_role in action.get("roles", []) or self.user_role == "superadmin"
            ]
        else:
            available = all_actions
        
        # Apply business logic filters
        filtered_actions = []
        for action in available:
            action_name = action.get("action")
            
            # Business rule: Completed orders cannot be reassigned
            if action_name == "reassign_order" and current_status in ["completed", "closed", "archived"]:
                continue  # Skip this action
            
            # Business rule: Closed/archived orders have limited edit capabilities
            if action_name in ["edit_order", "update_order"] and current_status in ["closed", "archived"]:
                # Allow edit for closed/archived but mark as restricted
                action["restricted"] = True
                action["reason"] = "Order is in final state - edits are for corrections only"
            
            # Business rule: Cancelled orders can only be reopened or refunded
            if current_status == "cancelled" and action_name not in ["reopen_order", "refund_order", "edit_order"]:
                if action_name != "update_order":  # Allow update for corrections
                    continue
            
            # Business rule: Refunded orders can only be closed
            if current_status == "refunded" and action_name not in ["close_order", "edit_order"]:
                if action_name != "update_order":  # Allow update for corrections
                    continue
            
            filtered_actions.append(action)
        
        # Add additional context
        for action in filtered_actions:
            action["available"] = True
            action["current_status"] = current_status
            
            # Check if transition is valid
            target_status = action.get("target_status")
            if target_status:
                # Check if transition is in valid transitions
                allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
                action["can_transition"] = target_status in allowed_transitions
                if not action["can_transition"]:
                    action["reason"] = f"Cannot transition from '{current_status}' to '{target_status}'"
            else:
                action["can_transition"] = True
        
        return filtered_actions
    
    def execute_action(
        self,
        order: Order,
        action_name: str,
        reason: str = None,
        **params
    ) -> Order:
        """
        Execute an action on an order and automatically trigger status transition if needed.
        
        Args:
            order: The order instance
            action_name: Name of the action to execute
            **params: Additional parameters for the action
            
        Returns:
            Updated order instance
            
        Raises:
            ValueError: If action is not available for current state
            ValidationError: If transition is not allowed
        """
        # Get available actions
        available_actions = self.get_available_actions(order)
        action_config = next(
            (a for a in available_actions if a["action"] == action_name),
            None
        )
        
        if not action_config:
            raise ValueError(
                f"Action '{action_name}' is not available for order in status '{order.status}'"
            )
        
        # Check if user has permission
        if self.user_role and self.user_role != "superadmin":
            if self.user_role not in action_config.get("roles", []):
                raise ValidationError(
                    f"User role '{self.user_role}' does not have permission to perform '{action_name}'"
                )
        
        # Build reason for transition (use provided reason or default)
        transition_reason = reason or f"Action: {action_name}"
        if reason:
            transition_reason = f"{action_name}: {reason}"
        
        # Execute the action via dispatcher
        from orders.dispatcher import OrderActionDispatcher
        try:
            # For mark_paid action, extract reference_id and payment_method
            if action_name == "mark_paid":
                reference_id = params.pop("reference_id", None)
                payment_method = params.pop("payment_method", None)
                if reference_id:
                    params["reference_id"] = reference_id
                if payment_method:
                    params["payment_method"] = payment_method
            
            updated_order = OrderActionDispatcher.dispatch(
                action_name=action_name,
                order_id=order.id,
                actor=self.user,
                reason=reason,
                **params
            )
        except Exception as e:
            # If action doesn't exist, try direct transition
            target_status = action_config.get("target_status")
            if target_status:
                transition_service = StatusTransitionService(user=self.user)
                updated_order = transition_service.transition_order_to_status(
                    order,
                    target_status,
                    reason=transition_reason
                )
            else:
                raise ValueError(f"Action '{action_name}' failed: {str(e)}")
        
        # If action has a target status and order hasn't transitioned, do it now
        target_status = action_config.get("target_status")
        if target_status and updated_order.status != target_status:
            transition_service = StatusTransitionService(user=self.user)
            try:
                updated_order = transition_service.transition_order_to_status(
                    updated_order,
                    target_status,
                    reason=transition_reason
                )
            except Exception as e:
                # Transition failed, but action might have succeeded
                # Log warning but don't fail
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Action {action_name} succeeded but transition to {target_status} failed: {str(e)}")
        
        return updated_order
    
    def can_perform_action(self, order: Order, action_name: str) -> tuple[bool, Optional[str]]:
        """
        Check if a user can perform a specific action on an order.
        
        Returns:
            (can_perform, reason_if_not)
        """
        available_actions = self.get_available_actions(order)
        action_config = next(
            (a for a in available_actions if a["action"] == action_name),
            None
        )
        
        if not action_config:
            return False, f"Action '{action_name}' is not available for status '{order.status}'"
        
        if self.user_role and self.user_role != "superadmin":
            if self.user_role not in action_config.get("roles", []):
                return False, f"User role '{self.user_role}' cannot perform this action"
        
        if not action_config.get("can_transition", True):
            return False, action_config.get("reason", "Transition not allowed")
        
        return True, None

