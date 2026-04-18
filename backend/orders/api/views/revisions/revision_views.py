from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.revision_permissions import (
    CanRequestRevision,
)
from orders.api.serializers.revisions.revision_request_serializer import (
    RevisionRequestSerializer,
)
from orders.models import Order
from orders.services.revision_orchestration_service import (
    RevisionOrchestrationService,
)


class RevisionRequestView(GenericAPIView):
    """
    Route a revision request into free revision or paid adjustment.
    """

    serializer_class = RevisionRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanRequestRevision,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        result = RevisionOrchestrationService.create_revision_request(
            order=order,
            requested_by=request.user,
            reason=validated_data["reason"],
            scope_summary=validated_data["scope_summary"],
            is_within_original_scope=validated_data[
                "is_within_original_scope"
            ],
            triggered_by=request.user,
        )

        if hasattr(result, "adjustment_type"):
            return Response(
                {
                    "message": "Revision routed to paid adjustment.",
                    "routing": "paid_adjustment",
                    "adjustment_request_id": result.pk,
                    "status": result.status,
                    "adjustment_type": result.adjustment_type,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Free revision request created.",
                "routing": "free_revision",
                "revision_request_id": result.pk,
                "status": result.status,
            },
            status=status.HTTP_201_CREATED,
        )

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