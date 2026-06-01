from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import CanRefundSpecialOrder
from special_orders.api.serializers import (
    SpecialOrderRefundApplicationSerializer,
)
from special_orders.selectors import SpecialOrderFundingSelector
from special_orders.services.new_services.special_order_refund_service import (
    SpecialOrderRefundService,
)

class ApplyRefundView(APIView):
    permission_classes = [IsAuthenticated, CanRefundSpecialOrder]

    def post(self, request, payment_application_id: int):
        data = cast(dict[str, Any], request.data)

        payment_application = (
            SpecialOrderFundingSelector.get_payment_application(
                website=request.user.website,
                payment_application_id=payment_application_id,
            )
        )

        self.check_object_permissions(request, payment_application)

        refund = SpecialOrderRefundService.apply_refund(
            payment_application=payment_application,
            amount=Decimal(str(data["amount"])),
            reason=str(data.get("reason", "")),
            approved_by=request.user,
            metadata=data.get("metadata", {}),
        )

        serializer = SpecialOrderRefundApplicationSerializer(refund)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

