from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Orders.
    """
    queryset = Order.objects.all().select_related('client', 'writer', 'preferred_writer', 'discount_code', 'website')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Return the queryset based on the user's role.
        - Admins and support can see all orders.
        - Clients can see only their orders.
        """
        user = self.request.user
        if user.is_staff:  # Admin or support
            return Order.objects.all()
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user as the client when creating an order.
        """
        serializer.save(client=self.request.user)

    def perform_update(self, serializer):
        """
        Additional logic during order updates (if required).
        """
        serializer.save()