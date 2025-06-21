from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.dispatcher import OrderActionDispatcher
from orders.permissions import IsOrderOwnerOrSupport


class OrderActionView(views.APIView):
    """
    Handles transitions on an order using the action dispatcher.

    The request must include the 'action' field and any additional
    parameters required by the specific order action.
    """

    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def post(self, request, pk: int):
        """
        Executes an action on a specific order.

        Args:
            request: The HTTP request object.
            pk (int): The ID of the target order.

        Returns:
            Response: JSON response indicating success or failure.
        """
        action = request.data.get("action")
        if not action:
            return Response(
                {"detail": "Missing 'action' field in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        params = request.data.copy()
        params.pop("action", None)

        try:
            updated_order = OrderActionDispatcher.dispatch(
                action_name=action,
                order_id=pk,
                **params
            )
            return Response(
                {
                    "status": "success",
                    "order_id": updated_order.id,
                    "new_status": updated_order.status
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