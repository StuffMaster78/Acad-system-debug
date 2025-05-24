from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.actions.dispatcher import OrderActionDispatcher
from orders.permissions import IsOrderOwnerOrSupport


class OrderActionView(views.APIView):
    """
    Handles transitions on an order using the action dispatcher.

    Requires the request body to contain the 'action' field and any
    additional params required by that specific action.
    """

    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def post(self, request, pk):
        """
        Executes an action on a specific order.

        Args:
            request: The HTTP request object.
            pk (int): The ID of the order.

        Returns:
            Response: JSON response with order data or error message.
        """
        action = request.data.get('action')
        data = request.data.copy()
        data['order_id'] = pk

        if not action:
            return Response(
                {"detail": "Missing 'action' in request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_order = OrderActionDispatcher.dispatch(action, data)
            return Response(
                {"status": "success", "order": updated_order.id},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )