from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from orders.api.serializers.unpaid_order_message_dispatch_serializer import (
    UnpaidOrderMessageDispatchSerializer,
)
from orders.models.legacy_models.unpaid_order_message_dispatch import (
    UnpaidOrderMessageDispatch,
)


class UnpaidOrderMessageDispatchListView(generics.ListAPIView):
    """
    List dispatch history for unpaid order reminders.
    """

    serializer_class = UnpaidOrderMessageDispatchSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Restrict dispatch history to the current tenant website.
        """
        queryset = UnpaidOrderMessageDispatch.objects.filter(
            website=self.request.user.website,
        ).select_related(
            "order",
            "client",
            "unpaid_order_message",
        ).order_by("-created_at", "-id")

        order_id = self.request.query_params.get("order_id")
        if order_id:
            queryset = queryset.filter(order_id=order_id)

        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset