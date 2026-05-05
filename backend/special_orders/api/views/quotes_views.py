from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanAcceptSpecialOrderQuote,
    CanManageSpecialOrderQuote,
)
from special_orders.api.serializers import (
    CreateSpecialOrderQuoteSerializer,
    RejectSpecialOrderQuoteSerializer,
    SpecialOrderPricingSnapshotSerializer,
    SpecialOrderQuoteSerializer,
)
from special_orders.selectors import (
    SpecialOrderQuoteSelector,
    SpecialOrderSelector,
)
from special_orders.services.new_services.special_order_quote_service import (
    SpecialOrderQuoteService,
)


class SpecialOrderQuoteDetailView(APIView):
    permission_classes = [IsAuthenticated, CanAcceptSpecialOrderQuote]

    def get(self, request, quote_id: int):
        quote = SpecialOrderQuoteSelector.get_by_id(
            website=request.user.website,
            quote_id=quote_id,
        )

        self.check_object_permissions(request, quote)

        serializer = SpecialOrderQuoteSerializer(quote)
        return Response(serializer.data)


class CreateSpecialOrderQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = CreateSpecialOrderQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        quote = SpecialOrderQuoteService.create_quote(
            special_order=special_order,
            line_items=data["line_items"],
            created_by=request.user,
            expires_at=data.get("expires_at"),
        )

        response_serializer = SpecialOrderQuoteSerializer(quote)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class SendSpecialOrderQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, quote_id: int):
        quote = SpecialOrderQuoteSelector.get_by_id(
            website=request.user.website,
            quote_id=quote_id,
        )

        self.check_object_permissions(request, quote.special_order)

        quote = SpecialOrderQuoteService.send_quote(
            quote=quote,
            sent_by=request.user,
        )

        serializer = SpecialOrderQuoteSerializer(quote)
        return Response(serializer.data)


class AcceptSpecialOrderQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanAcceptSpecialOrderQuote]

    def post(self, request, quote_id: int):
        quote = SpecialOrderQuoteSelector.get_by_id(
            website=request.user.website,
            quote_id=quote_id,
        )

        self.check_object_permissions(request, quote)

        snapshot = SpecialOrderQuoteService.accept_quote(
            quote=quote,
            accepted_by=request.user,
        )

        serializer = SpecialOrderPricingSnapshotSerializer(snapshot)
        return Response(serializer.data)


class RejectSpecialOrderQuoteView(APIView):
    permission_classes = [IsAuthenticated, CanAcceptSpecialOrderQuote]

    def post(self, request, quote_id: int):
        serializer = RejectSpecialOrderQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        quote = SpecialOrderQuoteSelector.get_by_id(
            website=request.user.website,
            quote_id=quote_id,
        )

        self.check_object_permissions(request, quote)

        quote = SpecialOrderQuoteService.reject_quote(
            quote=quote,
            rejected_by=request.user,
            reason=str(data.get("reason", "")),
        )

        response_serializer = SpecialOrderQuoteSerializer(quote)
        return Response(response_serializer.data)