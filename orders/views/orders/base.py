from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from orders.serializers import OrderSerializer
from orders.models import Order
from orders.services import OrderService
from orders.permissions import IsAssignedWriter, IsSupportOrAdmin

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="actions/(?P<action_name>[^/.]+)")
    def execute_action(self, request, pk=None, action_name=None):
        """
        Dynamically execute a registered order action via:
        /orders/{id}/actions/{action_name}/
        """
        order = self.get_object()
        action_cls = OrderActionRegistry.get(action_name)

        if not action_cls:
            return Response(
                {"detail": f"Action '{action_name}' is not supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if isinstance(action_cls, type):
                action_instance = action_cls(order, **request.data)
            else:
                # Just in case a functional handler is used
                return Response({"error": "Unsupported action handler type."}, status=500)

            result = action_instance.execute()

            return Response({"message": str(result)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)