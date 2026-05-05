from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanManageSpecialOrderQuote,
    CanViewSpecialOrder,
)
from special_orders.api.serializers.dispute_serializers import (
    DisputeResolutionSerializer,
    DisputeSerializer,
    OpenDisputeSerializer,
    RejectDisputeSerializer,
    ResolveDisputeSerializer,
)
from special_orders.models import (
    SpecialOrderDispute,
    SpecialOrderRefundApplication,
)
from special_orders.selectors import SpecialOrderSelector
from special_orders.services.new_services.special_order_dispute_service import (
    SpecialOrderDisputeService,
)


class OpenDisputeView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int):
        serializer = OpenDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        assigned_to = None
        assigned_to_id = data.get("assigned_to_id")
        if assigned_to_id is not None:
            User = get_user_model()
            assigned_to = User.objects.get(
                id=int(assigned_to_id),
                website=request.user.website,
            )

        dispute = SpecialOrderDisputeService.open_dispute(
            special_order=special_order,
            opened_by=request.user,
            title=str(data["title"]),
            description=str(data["description"]),
            assigned_to=assigned_to,
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(
            DisputeSerializer(dispute).data,
            status=status.HTTP_201_CREATED,
        )


class MarkDisputeUnderReviewView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, dispute_id: int):
        dispute = SpecialOrderDispute.objects.select_related(
            "special_order",
        ).get(
            id=dispute_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, dispute.special_order)

        dispute = SpecialOrderDisputeService.mark_under_review(
            dispute=dispute,
            reviewed_by=request.user,
        )

        return Response(DisputeSerializer(dispute).data)


class ResolveDisputeView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, dispute_id: int):
        serializer = ResolveDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        dispute = SpecialOrderDispute.objects.select_related(
            "special_order",
        ).get(
            id=dispute_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, dispute.special_order)

        refund_application = None
        refund_application_id = data.get("refund_application_id")
        if refund_application_id is not None:
            refund_application = SpecialOrderRefundApplication.objects.get(
                id=int(refund_application_id),
                website=request.user.website,
            )

        resolution = SpecialOrderDisputeService.resolve_dispute(
            dispute=dispute,
            resolution_type=str(data["resolution_type"]),
            resolved_by=request.user,
            notes=str(data.get("notes", "")),
            amount=data.get("amount"),
            refund_application=refund_application,
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(DisputeResolutionSerializer(resolution).data)


class RejectDisputeView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, dispute_id: int):
        serializer = RejectDisputeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        dispute = SpecialOrderDispute.objects.select_related(
            "special_order",
        ).get(
            id=dispute_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, dispute.special_order)

        dispute = SpecialOrderDisputeService.reject_dispute(
            dispute=dispute,
            rejected_by=request.user,
            reason=str(data["reason"]),
        )

        return Response(DisputeSerializer(dispute).data)