from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from orders.dispatcher import OrderActionDispatcher
from orders.permissions import IsOrderOwnerOrSupport
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services.order_action_service import OrderActionService


class OrderActionView(views.APIView):
    """
    Handles transitions on an order using the action dispatcher.
    Now with state-aware action system that automatically triggers transitions.
    
    Enhanced with:
    - Better error messages
    - Reason/notes support for audit trail
    - Detailed feedback for frontend modals
    - Optimized queries with select_related

    The request must include the 'action' field and any additional
    parameters required by the specific order action.
    """

    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def get_queryset(self):
        """Optimize order queries with select_related."""
        return Order.objects.select_related(
            'client',
            'assigned_writer',
            'website',
            'paper_type',
            'academic_level',
            'formatting_style',
            'subject',
            'type_of_work'
        )

    def post(self, request, pk: int):
        """
        Executes an action on a specific order.
        Actions automatically trigger appropriate status transitions.

        Args:
            request: The HTTP request object.
            pk (int): The ID of the target order.

        Body:
        {
            "action": "submit_order",
            "reason": "Optional reason for the action",
            "notes": "Optional notes for audit trail",
            "additional_params": {...}
        }

        Returns:
            Response: JSON response with updated order, status change, and detailed feedback.
        """
        action = request.data.get("action")
        if not action:
            return Response(
                {
                    "status": "error",
                    "detail": "Missing 'action' field in request body.",
                    "field": "action"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optimize query with select_related
        try:
            order = self.get_queryset().get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "detail": f"Order with ID {pk} not found.",
                    "order_id": pk
                },
                status=status.HTTP_404_NOT_FOUND
            )

        action_service = OrderActionService(user=request.user)
        
        # Check if action is available
        can_perform, reason = action_service.can_perform_action(order, action)
        if not can_perform:
            # Get available actions for better error message
            available_actions = action_service.get_available_actions(order)
            available_action_names = [a["action"] for a in available_actions]
            
            return Response(
                {
                    "status": "error",
                    "detail": reason or f"Action '{action}' is not available for order in status '{order.status}'",
                    "order_id": order.id,
                    "current_status": order.status,
                    "requested_action": action,
                    "available_actions": available_action_names,
                    "suggestion": f"Available actions: {', '.join(available_action_names) if available_action_names else 'None'}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        params = request.data.copy()
        params.pop("action", None)
        reason = params.pop("reason", None) or params.pop("notes", None)  # Support both fields

        try:
            with transaction.atomic():
                # Execute action with automatic transition
                updated_order = action_service.execute_action(
                    order=order,
                    action_name=action,
                    reason=reason,
                    **params
                )
                
                # Refresh from database to get latest state
                updated_order.refresh_from_db()
                
                # Determine user-friendly action label
                available_actions = action_service.get_available_actions(order)
                action_config = next(
                    (a for a in available_actions if a["action"] == action),
                    None
                )
                action_label = action_config.get("label", action.replace("_", " ").title()) if action_config else action.replace("_", " ").title()
                
                # Build success message
                status_changed = order.status != updated_order.status
                if status_changed:
                    message = f"Order #{order.id} {action_label.lower()}d successfully. Status changed from '{order.status}' to '{updated_order.status}'."
                else:
                    message = f"Order #{order.id} {action_label.lower()}d successfully."
                
                return Response(
                    {
                        "status": "success",
                        "message": message,
                        "action": action,
                        "action_label": action_label,
                        "order_id": updated_order.id,
                        "old_status": order.status,
                        "new_status": updated_order.status,
                        "status_changed": status_changed,
                        "order": OrderSerializer(updated_order, context={"request": request}).data,
                        "reason": reason  # Echo back reason for confirmation
                    },
                    status=status.HTTP_200_OK
                )
        except ValueError as ve:
            return Response(
                {
                    "status": "error",
                    "detail": str(ve),
                    "order_id": order.id,
                    "action": action
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing order action {action} on order {pk}: {str(e)}", exc_info=True)
            
            return Response(
                {
                    "status": "error",
                    "detail": "An unexpected error occurred while processing your request.",
                    "error": str(e) if request.user.role in ["admin", "superadmin"] else None,  # Only show details to admins
                    "order_id": order.id,
                    "action": action
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, pk: int):
        """
        Get available actions for an order based on its current state.
        
        Returns:
            Response: List of available actions with metadata
        """
        try:
            order = self.get_queryset().get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "detail": f"Order with ID {pk} not found.",
                    "order_id": pk
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        action_service = OrderActionService(user=request.user)
        available_actions = action_service.get_available_actions(order)
        
        return Response(
            {
                "status": "success",
                "order_id": order.id,
                "current_status": order.status,
                "available_actions": available_actions,
                "user_role": getattr(request.user, "role", None)
            },
            status=status.HTTP_200_OK
        )
