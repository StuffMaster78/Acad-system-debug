from rest_framework import generics, permissions
from orders.models import OrderTransitionLog
from orders.serializers import OrderTransitionLogSerializer

class OrderTransitionLogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = OrderTransitionLogSerializer

    def get_queryset(self):
        queryset = OrderTransitionLog.objects.all()
        order_id = self.request.query_params.get("order")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset