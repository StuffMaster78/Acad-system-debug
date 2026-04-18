from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.dispute_permissions import (
    CanCloseDispute,
    CanEscalateDispute,
    CanOpenDispute,
    CanResolveDispute,
)
from orders.api.serializers.disputes.dispute_close_serializer import (
    DisputeCloseSerializer,
)
from orders.api.serializers.disputes.dispute_escalate_serializer import (
    DisputeEscalateSerializer,
)
from orders.api.serializers.disputes.dispute_open_serializer import (
    DisputeOpenSerializer,
)
from orders.api.serializers.disputes.dispute_resolve_serializer import (
    DisputeResolveSerializer,
)
from orders.models import Order, OrderDispute
from orders.services.dispute_orchestration_service import (
    DisputeOrchestrationService,
)


class DisputeOpenView(GenericAPIView):
    """
    Open a dispute for an eligible order.
    """

    serializer_class = DisputeOpenSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanOpenDispute,
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

        dispute = DisputeOrchestrationService.open_dispute(
            order=order,
            opened_by=request.user,
            reason=validated_data["reason"],
            summary=validated_data["summary"],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Dispute opened.",
                "dispute_id": dispute.pk,
                "order_id": order.pk,
                "status": dispute.status,
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


class DisputeEscalateView(GenericAPIView):
    """
    Escalate an open dispute.
    """

    serializer_class = DisputeEscalateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanEscalateDispute,
    ]

    def post(
        self,
        request: Request,
        dispute_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        dispute = self._get_dispute_for_tenant(
            request=request,
            dispute_id=dispute_id,
        )
        self.check_object_permissions(request, dispute)

        updated_dispute = DisputeOrchestrationService.escalate_dispute(
            dispute=dispute,
            escalated_by=request.user,
            notes=validated_data.get("notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Dispute escalated.",
                "dispute_id": updated_dispute.pk,
                "status": updated_dispute.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_dispute_for_tenant(
        *,
        request: Request,
        dispute_id: int,
    ) -> OrderDispute:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderDispute.objects.select_related(
                "website",
                "order",
                "opened_by",
            ),
            pk=dispute_id,
            website=user.website,
        )


class DisputeResolveView(GenericAPIView):
    """
    Resolve a dispute and record the outcome.
    """

    serializer_class = DisputeResolveSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanResolveDispute,
    ]

    def post(
        self,
        request: Request,
        dispute_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        dispute = self._get_dispute_for_tenant(
            request=request,
            dispute_id=dispute_id,
        )
        self.check_object_permissions(request, dispute)

        resolution = DisputeOrchestrationService.resolve_dispute(
            dispute=dispute,
            resolved_by=request.user,
            outcome=validated_data["outcome"],
            resolution_summary=validated_data["resolution_summary"],
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Dispute resolved.",
                "resolution_id": resolution.pk,
                "dispute_id": dispute.pk,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_dispute_for_tenant(
        *,
        request: Request,
        dispute_id: int,
    ) -> OrderDispute:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderDispute.objects.select_related(
                "website",
                "order",
                "opened_by",
            ),
            pk=dispute_id,
            website=user.website,
        )


class DisputeCloseView(GenericAPIView):
    """
    Close a resolved dispute and restore the order status.
    """

    serializer_class = DisputeCloseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCloseDispute,
    ]

    def post(
        self,
        request: Request,
        dispute_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        dispute = self._get_dispute_for_tenant(
            request=request,
            dispute_id=dispute_id,
        )
        self.check_object_permissions(request, dispute)

        updated_dispute = DisputeOrchestrationService.close_dispute(
            dispute=dispute,
            closed_by=request.user,
            restore_order_status=validated_data["restore_order_status"],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Dispute closed.",
                "dispute_id": updated_dispute.pk,
                "status": updated_dispute.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_dispute_for_tenant(
        *,
        request: Request,
        dispute_id: int,
    ) -> OrderDispute:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderDispute.objects.select_related(
                "website",
                "order",
                "opened_by",
            ),
            pk=dispute_id,
            website=user.website,
        )