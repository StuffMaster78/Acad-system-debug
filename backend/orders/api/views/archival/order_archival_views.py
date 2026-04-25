from __future__ import annotations

from typing import Any, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.api.serializers.archival.order_archival_serializer import (
    OrderArchiveActionSerializer,
)
from orders.models.orders.order import Order
from orders.services.order_archival_service import (
    OrderArchivalService,
)
from orders.api.permissions.order_archival_permissions import (
    CanArchiveOrder,
)

class OrderArchivalData(TypedDict, total=False):
    reason: str


class OrderArchivalView(APIView):
    """
    Explicitly archive a single order.
    """

    permission_classes = [permissions.IsAuthenticated, CanArchiveOrder]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = get_object_or_404(
            Order.objects.select_related("website", "client"),
            pk=order_id,
            website=request.user.website,
        )

        self.check_object_permissions(request, order)

        serializer = OrderArchiveActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(OrderArchivalData, serializer.validated_data)

        archived_order = OrderArchivalService.archive_order(
            order=order,
            archived_by=request.user,
            triggered_by=request.user,
            reason=data.get("reason", ""),
        )

        archived_at = getattr(archived_order, "archived_at", None)

        return Response(
            {
                "detail": "Order archived successfully.",
                "order_id": archived_order.pk,
                "status": archived_order.status,
                "archived_at": (
                    archived_at.isoformat()
                    if archived_at is not None
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )