from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments_processor.api.serializers.payment_checkout_serializer import (
    PaymentCheckoutSerializer,
)
from payments_processor.api.serializers.payment_intent_serializer import (
    PaymentIntentSerializer,
)
from payments_processor.services.payment_intent_service import PaymentIntentService


class PaymentCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        provider = str(validated_data["provider"])
        purpose = str(validated_data["purpose"])
        amount = cast(Decimal, validated_data["amount"])
        currency = str(validated_data.get("currency", "USD"))
        metadata = cast(dict[str, Any], validated_data.get("metadata", {}))

        result = PaymentIntentService.create_intent(
            customer=request.user,
            provider=provider,
            purpose=purpose,
            amount=amount,
            currency=currency,
            metadata=metadata,
        )

        payment_intent = result["payment_intent"]
        provider_data = result["provider_data"]

        return Response(
            {
                "payment_intent": PaymentIntentSerializer(payment_intent).data,
                "provider_data": provider_data,
            },
            status=status.HTTP_201_CREATED,
        )