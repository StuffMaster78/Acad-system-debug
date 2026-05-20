from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.lifecycle_permissions import (
    CanViewOrderLifecycle,
)
from orders.models import Order
from orders.services.order_monitoring_service import (
    OrderMonitoringService,
)


class OrderMonitoringView(GenericAPIView):
    """
    Return derived operational monitoring state for a single order.

    This endpoint exposes:
        1. Whether the order is late.
        2. Whether the order is critical.
        3. Remaining time to the writer deadline.
        4. A compact state label for dashboard use.
    """

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
        """
        Return monitoring state for a tenant-scoped order.

        Args:
            request:
                Incoming DRF request.
            order_id:
                Target order primary key.

        Returns:
            Response:
                Serialized monitoring snapshot.
        """
        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        operational_state = (
            OrderMonitoringService.build_operational_state(
                order=order,
            )
        )
        state_payload = (
            asdict(operational_state)
            if is_dataclass(operational_state)
            else vars(operational_state)
            if hasattr(operational_state, "__dict__")
            else operational_state
        )

        return Response(
            {
                "order_id": order.pk,
                **state_payload,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        """
        Return a tenant-scoped order for monitoring.

        Args:
            request:
                Incoming DRF request.
            order_id:
                Target order primary key.

        Returns:
            Order:
                Tenant-scoped order instance.
        """
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
