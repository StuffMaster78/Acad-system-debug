from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from orders.dispatcher import OrderActionDispatcher
from orders.permissions import IsOrderOwnerOrSupport
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services.order_action_service import OrderActionService


class OrderActionView(views.APIView):
    """
    Handles transitions on an order using the action dispatcher.
    Now with state-aware action system that automatically triggers transitions.

    The request must include the 'action' field and any additional
    parameters required by the specific order action.
    """

    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

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
            "additional_params": {...}
        }

        Returns:
            Response: JSON response with updated order and new status.
        """
        action = request.data.get("action")
        if not action:
            return Response(
                {"detail": "Missing 'action' field in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, pk=pk)
        action_service = OrderActionService(user=request.user)
        
        # Check if action is available
        can_perform, reason = action_service.can_perform_action(order, action)
        if not can_perform:
            return Response(
                {"detail": reason or f"Action '{action}' is not available"},
                status=status.HTTP_400_BAD_REQUEST
            )

        params = request.data.copy()
        params.pop("action", None)

        try:
            # Execute action with automatic transition
            updated_order = action_service.execute_action(
                order=order,
                action_name=action,
                **params
            )
            
            return Response(
                {
                    "status": "success",
                    "message": f"Action '{action}' executed successfully",
                    "order_id": updated_order.id,
                    "old_status": order.status,
                    "new_status": updated_order.status,
                    "order": OrderSerializer(updated_order, context={"request": request}).data
                },
                status=status.HTTP_200_OK
            )
        except ValueError as ve:
            return Response(
                {"detail": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, pk: int):
        """
        Get available actions for an order based on its current state.
        
        Returns:
            Response: List of available actions with metadata
        """
        order = get_object_or_404(Order, pk=pk)
        action_service = OrderActionService(user=request.user)
        available_actions = action_service.get_available_actions(order)
        
        return Response(
            {
                "order_id": order.id,
                "current_status": order.status,
                "available_actions": available_actions
            },
            status=status.HTTP_200_OK
        )
