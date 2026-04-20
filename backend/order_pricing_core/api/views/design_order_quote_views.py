"""
Design order quote API views.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.api.serializers.design_order_quote_serializers import (
    DesignOrderQuoteRequestSerializer,
)
from order_pricing_core.constants import QuoteMode
from order_pricing_core.services.quote_service import QuoteOperationResult
from order_pricing_core.services.quote_service import PricingQuoteService


class DesignOrderQuoteStartView(APIView):
    """
    Start a design order quote session.
    """

    def post(self, request: Request) -> Response:
        """
        Create an estimate-mode design order quote.
        """
        serializer = DesignOrderQuoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        result: QuoteOperationResult = PricingQuoteService.start_quote(
            website=request.website,
            service_code=str(data["service_code"]),
            payload=data,
            created_by=(
                request.user if request.user.is_authenticated else None
            ),
            mode=QuoteMode.ESTIMATE,
        )

        return Response(
            {
                "session_id": str(result.quote.session_id),
                "status": result.status,
                "estimated_min_price": result.estimated_min_price,
                "estimated_max_price": result.estimated_max_price,
                "currency": result.currency,
            },
            status=status.HTTP_201_CREATED,
        )


class DesignOrderQuoteUpdateView(APIView):
    """
    Update a design order quote session.
    """

    def post(self, request: Request, session_id: str) -> Response:
        """
        Recalculate a design order quote in final mode.
        """
        serializer = DesignOrderQuoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        quote = PricingQuoteService.get_quote_by_session_id(
            session_id=session_id,
        )

        result: QuoteOperationResult = PricingQuoteService.update_quote(
            quote=quote,
            payload=data,
            step=2,
            mode=QuoteMode.FINAL,
        )

        return Response(
            {
                "session_id": str(result.quote.session_id),
                "status": result.status,
                "current_step": result.current_step,
                "calculated_price": result.calculated_price,
                "currency": result.currency,
                "lines": [
                    {
                        "line_type": line.line_type,
                        "code": line.code,
                        "label": line.label,
                        "amount": line.amount,
                        "metadata": line.metadata,
                    }
                    for line in result.lines
                ],
            },
            status=status.HTTP_200_OK,
        )