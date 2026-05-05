from __future__ import annotations

from typing import Any, cast

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.serializers.pricing_preview_serializers import (
    FixedSpecialOrderPricingPreviewSerializer,
)
from special_orders.integrations.discount_bridge import (
    SpecialOrderDiscountBridge,
)
from special_orders.models import (
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
)
from special_orders.services.new_services.special_order_fixed_pricing_service import (
    SpecialOrderFixedPricingService,
)


class FixedSpecialOrderPricingPreviewView(APIView):
    """
    Preview price before creating a fixed special order.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FixedSpecialOrderPricingPreviewSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        config = PredefinedSpecialOrderConfig.objects.get(
            id=int(data["predefined_config_id"]),
            website=request.user.website,
        )

        duration = PredefinedSpecialOrderDuration.objects.get(
            id=int(data["predefined_duration_id"]),
            website=request.user.website,
        )

        gross_quote = SpecialOrderFixedPricingService.calculate_gross_price(
            predefined_config=config,
            predefined_duration=duration,
            currency=str(data.get("currency", "USD")),
            platform=str(data.get("platform", "")),
            writer_level=str(data.get("writer_level", "")),
        )

        discount_result = SpecialOrderDiscountBridge.apply_discount(
            website=request.user.website,
            client=request.user,
            gross_amount=gross_quote.gross_amount,
            currency=gross_quote.currency,
            coupon_code=str(data.get("coupon_code", "")),
        )

        return Response(
            {
                "currency": gross_quote.currency,
                "base_price": str(gross_quote.base_price),
                "gross_amount": str(gross_quote.gross_amount),
                "discount_amount": str(discount_result.discount_amount),
                "final_amount": str(discount_result.final_amount),
                "line_items": gross_quote.line_items,
                "discount": {
                    "reference": discount_result.discount_reference,
                    "metadata": discount_result.metadata,
                },
                "metadata": gross_quote.metadata,
            }
        )