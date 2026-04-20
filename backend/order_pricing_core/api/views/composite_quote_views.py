"""
Composite quote API views for the order_pricing_core app.
"""

from __future__ import annotations

from typing import Any
from typing import cast
from uuid import UUID

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.api.serializers.composite_quote_serializers import (
    CompositeQuoteCreateSerializer,
)
from order_pricing_core.api.serializers.composite_quote_serializers import (
    CompositeQuoteFinalizeSerializer,
)
from order_pricing_core.models import CompositePricingQuote
from order_pricing_core.models import CompositePricingQuoteItem
from order_pricing_core.services.composite_quote_service import (
    CompositeFinalizeResult,
)
from order_pricing_core.services.composite_quote_service import (
    CompositePricingQuoteService,
)
from order_pricing_core.services.quote_service import PricingQuoteService


class CompositeQuoteCreateView(APIView):
    """
    Create a composite quote from component quote sessions.
    """

    def post(self, request: Request) -> Response:
        """
        Create a composite quote.
        """
        serializer = CompositeQuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        component_session_ids = cast(list[UUID], data["component_session_ids"])

        component_quotes = [
            PricingQuoteService.get_quote_by_session_id(
                session_id=session_id,
            )
            for session_id in component_session_ids
        ]

        composite_quote = CompositePricingQuoteService.create_composite_quote(
            website=request.website,
            component_quotes=component_quotes,
            created_by=(
                request.user if request.user.is_authenticated else None
            ),
        )

        return Response(
            self._serialize_composite_quote(composite_quote),
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _serialize_composite_quote(
        composite_quote: CompositePricingQuote,
    ) -> dict[str, Any]:
        """
        Serialize a composite quote response payload.
        """
        items = CompositePricingQuoteService.get_items(composite_quote)

        return {
            "session_id": str(composite_quote.session_id),
            "currency": composite_quote.currency,
            "subtotal": composite_quote.subtotal,
            "discount_amount": composite_quote.discount_amount,
            "total": composite_quote.total,
            "is_final": composite_quote.is_final,
            "items": [
                CompositeQuoteCreateView._serialize_item(item)
                for item in items
            ],
        }

    @staticmethod
    def _serialize_item(
        item: CompositePricingQuoteItem,
    ) -> dict[str, Any]:
        """
        Serialize one composite quote item.
        """
        return {
            "pricing_quote_session_id": str(
                item.pricing_quote.session_id
            ),
            "service_code": item.service.service_code,
            "service_name": item.service.name,
            "component_label": item.component_label,
            "subtotal": item.subtotal,
            "total": item.total,
            "sort_order": item.sort_order,
        }


class CompositeQuoteDetailView(APIView):
    """
    Retrieve a composite quote by session id.
    """

    def get(self, request: Request, session_id: str) -> Response:
        """
        Return composite quote details.
        """
        composite_quote = CompositePricingQuoteService.get_by_session_id(
            session_id=session_id,
        )

        return Response(
            CompositeQuoteCreateView._serialize_composite_quote(
                composite_quote
            ),
            status=status.HTTP_200_OK,
        )


class CompositeQuoteUpdateView(APIView):
    """
    Replace component quotes for an existing composite quote.
    """

    def post(self, request: Request, session_id: str) -> Response:
        """
        Update a composite quote.
        """
        serializer = CompositeQuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        component_session_ids = cast(list[UUID], data["component_session_ids"])

        composite_quote = CompositePricingQuoteService.get_by_session_id(
            session_id=session_id,
        )

        component_quotes = [
            PricingQuoteService.get_quote_by_session_id(
                session_id=component_session_id,
            )
            for component_session_id in component_session_ids
        ]

        updated_quote = CompositePricingQuoteService.update_composite_quote(
            composite_quote=composite_quote,
            component_quotes=component_quotes,
        )

        return Response(
            CompositeQuoteCreateView._serialize_composite_quote(
                updated_quote
            ),
            status=status.HTTP_200_OK,
        )


class CompositeQuoteFinalizeView(APIView):
    """
    Finalize a composite quote into component snapshots.
    """

    def post(self, request: Request, session_id: str) -> Response:
        """
        Finalize a composite quote.
        """
        serializer = CompositeQuoteFinalizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        composite_quote = CompositePricingQuoteService.get_by_session_id(
            session_id=session_id,
        )

        result: CompositeFinalizeResult = (
            CompositePricingQuoteService.finalize_composite_quote(
                composite_quote=composite_quote,
                related_object_type=data.get("related_object_type", ""),
                related_object_id=data.get("related_object_id", ""),
                created_by=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
            )
        )

        return Response(
            {
                "session_id": str(result.composite_quote.session_id),
                "subtotal": result.subtotal,
                "discount_amount": result.discount_amount,
                "total": result.total,
                "currency": result.currency,
                "component_snapshot_ids": [
                    snapshot.pk
                    for snapshot in result.component_snapshots
                ],
                "is_final": result.composite_quote.is_final,
            },
            status=status.HTTP_200_OK,
        )