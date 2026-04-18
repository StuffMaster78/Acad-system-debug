from __future__ import annotations

from dataclasses import asdict
from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.lifecycle_permissions import (
    CanViewOrderLifecycle,
)
from orders.api.serializers.lifecycle.order_lifecycle_snapshot_serializer import (  # noqa: E501
    OrderLifecycleSnapshotSerializer,
)
from orders.models import Order
from orders.services.order_lifecycle_read_service import (
    OrderLifecycleReadService,
)


class OrderLifecycleView(GenericAPIView):
    """
    Return a consolidated lifecycle snapshot for an order.
    """

    serializer_class = OrderLifecycleSnapshotSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOrderLifecycle,
    ]

    def get(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        snapshot = OrderLifecycleReadService.build_snapshot(order=order)
        serializer = self.get_serializer(asdict(snapshot))

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related(
                "website",
                "client",
                "preferred_writer",
            ),
            pk=order_id,
            website=user.website,
        )