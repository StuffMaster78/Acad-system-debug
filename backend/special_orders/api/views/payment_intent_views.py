from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import CanPaySpecialOrder
from special_orders.selectors import SpecialOrderSelector
from special_orders.integrations.payment_intent_bridge import (
    SpecialOrderPaymentIntentBridge,
)


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated, CanPaySpecialOrder]

    def post(self, request, special_order_id: int):
        data = cast(dict[str, Any], request.data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        intent_data = (
            SpecialOrderPaymentIntentBridge.create_external_payment_intent(
                special_order=special_order,
                amount=Decimal(str(data["amount"])),
                provider=data.get("provider"),
                created_by=request.user,
                metadata=data.get("metadata", {}),
            )
        )

        return Response(
            {
                "payment_intent_id": intent_data["payment_intent"].id,
                "reference": intent_data["payment_intent"].reference,
                "provider_data": intent_data["provider_data"],
            },
            status=status.HTTP_201_CREATED,
        )