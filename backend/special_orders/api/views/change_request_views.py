from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanManageSpecialOrderQuote,
    CanViewSpecialOrder,
)
from special_orders.api.serializers.change_request_serializers import (
    ChangeRequestQuoteSerializer,
    ChangeRequestSerializer,
    CreateChangeQuoteSerializer,
    CreateChangeRequestSerializer,
    ReviewChangeRequestSerializer,
)
from special_orders.models import (
    SpecialOrderChangeRequest,
    SpecialOrderChangeRequestQuote,
)
from special_orders.selectors import SpecialOrderSelector
from special_orders.services.new_services.special_order_change_request_service import (
    SpecialOrderChangeRequestService,
)


class CreateChangeRequestView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int):
        serializer = CreateChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        change_request = SpecialOrderChangeRequestService.create_request(
            special_order=special_order,
            requested_by=request.user,
            title=str(data["title"]),
            description=str(data["description"]),
            pricing_impact=str(
                data.get("pricing_impact", "additional_charge")
            ),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(
            ChangeRequestSerializer(change_request).data,
            status=status.HTTP_201_CREATED,
        )


class ReviewChangeRequestView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, change_request_id: int):
        serializer = ReviewChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        change_request = SpecialOrderChangeRequest.objects.select_related(
            "special_order",
        ).get(
            id=change_request_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, change_request.special_order)

        change_request = SpecialOrderChangeRequestService.review_request(
            change_request=change_request,
            reviewed_by=request.user,
            approve=bool(data["approve"]),
            decision_reason=str(data.get("decision_reason", "")),
            estimated_amount=data.get("estimated_amount"),
        )

        return Response(ChangeRequestSerializer(change_request).data)


class CreateChangeQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, change_request_id: int):
        serializer = CreateChangeQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        change_request = SpecialOrderChangeRequest.objects.select_related(
            "special_order",
        ).get(
            id=change_request_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, change_request.special_order)

        quote = SpecialOrderChangeRequestService.create_change_quote(
            change_request=change_request,
            amount=data["amount"],
            created_by=request.user,
            expires_at=data.get("expires_at"),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(
            ChangeRequestQuoteSerializer(quote).data,
            status=status.HTTP_201_CREATED,
        )


class AcceptChangeQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, change_quote_id: int):
        quote = SpecialOrderChangeRequestQuote.objects.select_related(
            "change_request",
            "change_request__special_order",
        ).get(
            id=change_quote_id,
            website=request.user.website,
        )

        self.check_object_permissions(
            request,
            quote.change_request.special_order,
        )

        milestone = SpecialOrderChangeRequestService.accept_change_quote(
            quote=quote,
            accepted_by=request.user,
        )

        return Response(
            {
                "milestone_id": milestone.id,
                "amount_due": str(milestone.amount_due),
                "status": milestone.status,
            },
            status=status.HTTP_201_CREATED,
        )