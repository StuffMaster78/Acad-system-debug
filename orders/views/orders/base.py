from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.permissions import IsOrderOwnerOrSupport


class OrderBaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Base viewset for orders. Supports list and retrieve operations.

    Attributes:
        queryset: QuerySet of Order objects.
        serializer_class: Serializer used for order objects.
        permission_classes: List of permission classes.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def get_queryset(self):
        """
        Returns the filtered queryset for the current user.

        Returns:
            QuerySet: A queryset filtered based on user role.
        """
        user = self.request.user

        if user.is_superuser:
            return Order.objects.all()

        if user.role == 'client':
            return Order.objects.filter(client=user)

        if user.role == 'writer':
            return Order.objects.filter(writer=user)

        if user.role in ['admin', 'support', 'editor']:
            return Order.objects.all()

        return Order.objects.none()