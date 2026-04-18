from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.approval_permissions import (
    CanApproveOrder,
)
from orders.api.serializers.approval.approve_order_serializer import (
    ApproveOrderSerializer,
)
from orders.models import Order
from orders.services.order_approval_service import (
    OrderApprovalService,
)


class ApproveOrderView(GenericAPIView):
    """
    Allow a client owner or staff actor to explicitly approve an order.

    This endpoint completes the submitted order through the approval
    workflow. Review capture should be handled separately by the
    reviews app after approval.
    """

    serializer_class = ApproveOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanApproveOrder,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Explicitly approve a submitted order.

        Args:
            request:
                Incoming DRF request.
            order_id:
                Target order primary key.

        Returns:
            Response:
                Serialized approval result.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        updated_order = OrderApprovalService.approve_order(
            order=order,
            approved_by=request.user,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Order approved successfully.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "approved_at": updated_order.approved_at,
                "completed_at": updated_order.completed_at,
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
        Return a tenant-scoped order for approval.

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