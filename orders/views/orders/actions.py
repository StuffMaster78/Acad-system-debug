# orders/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from orders.models import Order
from orders.actions.dispatcher import dispatch_order_action
from orders.serializers import OrderActionSerializer

class OrderActionViewSet(viewsets.ViewSet):
    """
    A ViewSet that dispatches order actions to the appropriate handlers.
    """

    def dispatch_action(self, action_name, order_id):
        """
        Dispatches the action on the order.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError({"error": "Order not found"})

        try:
            dispatch_order_action(action_name, order)
            return Response({"status": "success", "message": f"Action '{action_name}' performed successfully on order {order_id}"})
        except ValidationError as e:
            raise ValidationError({"error": str(e)})
        except Exception as e:
            raise ValidationError({"error": f"Unexpected error: {str(e)}"})

    def create(self, request):
        """
        Perform an action on an order based on the provided action and order ID.
        """
        serializer = OrderActionSerializer(data=request.data)
        if serializer.is_valid():
            action_name = serializer.validated_data['action']
            order_id = serializer.validated_data['order_id']
            return self.dispatch_action(action_name, order_id)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)