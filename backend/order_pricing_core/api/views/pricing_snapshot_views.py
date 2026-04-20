"""
Pricing snapshot API views.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.api.serializers.snapshot_serializers import (
    PricingSnapshotCreateSerializer,
)
from order_pricing_core.services.quote_service import PricingQuoteService
from order_pricing_core.services.snapshot_service import (
    PricingSnapshotService,
)


class PricingSnapshotCreateView(APIView):
    """
    Create a frozen pricing snapshot from a quote.
    """

    def post(self, request: Request, session_id: str) -> Response:
        """
        Finalize a quote into a pricing snapshot.
        """
        serializer = PricingSnapshotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        quote = PricingQuoteService.get_quote_by_session_id(
            session_id=session_id,
        )

        snapshot = PricingSnapshotService.create_snapshot(
            quote=quote,
            related_object_type=data.get("related_object_type", ""),
            related_object_id=data.get("related_object_id", ""),
            created_by=(
                request.user if request.user.is_authenticated else None
            ),
        )

        return Response(
            {
                "snapshot_id": snapshot.pk,
                "final_price": snapshot.final_price,
                "currency": snapshot.currency,
            },
            status=status.HTTP_201_CREATED,
        )