from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from orders.permissions import IsStaffOrRequestOwner

from orders.models import OrderRequest
from orders.serializers import OrderRequestSerializer, WriterRequestActionSerializer
from orders.registry.decorator import get_registered_action as get_action_by_name

class OrderRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin/staff viewset to manage writer requests on orders.
    All business logic is offloaded to action classes.
    """
    queryset = OrderRequest.objects.select_related("order", "writer")
    serializer_class = OrderRequestSerializer
    permission_classes = [IsAuthenticated, IsStaffOrRequestOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(writer=user)

    @action(detail=False, methods=["post"], url_path="action")
    def perform_action(self, request):
        """
        Dynamic action endpoint — passes control to relevant Action class.
        Payload:
        {
            "action": "accept_request",
            "order_id": 12,
            "data": {
                "request": 45
            }
        }
        """
        serializer = WriterRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"detail": "Missing order_id."}, status=400)

        from orders.models import Order
        order = Order.objects.get(id=order_id)

        result = serializer.execute(user=request.user, order=order)
        return Response(OrderRequestSerializer(result).data, status=status.HTTP_200_OK)