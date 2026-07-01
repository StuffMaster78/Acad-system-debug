from __future__ import annotations

import dataclasses
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
from payments_processor.services.payment_application_service import PaymentApplicationService
from payments_processor.enums import PaymentIntentStatus
from payments_processor.models import PaymentIntent


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
            client=request.user,
            provider=provider,
            purpose=purpose,
            amount=amount,
            currency=currency,
            metadata=metadata,
            website=getattr(request, "website", None),
        )

        payment_intent = result["payment_intent"]
        provider_data = result["provider_data"]

        return Response(
            {
                "payment_intent": PaymentIntentSerializer(payment_intent).data,
                "provider_data": dataclasses.asdict(provider_data),
            },
            status=status.HTTP_201_CREATED,
        )


class CancelPrewarmView(APIView):
    """
    Cancel a pre-warmed (unlinked) PaymentIntent created for ORDER pre-warming.

    Only cancels if:
    - The intent belongs to the requesting client
    - Status is still PENDING (not yet paid or linked to an order)
    - payable (order) is not yet linked
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from payments_processor.models import PaymentIntent
        reference = str(request.data.get("reference", "")).strip()
        if not reference:
            return Response({"detail": "reference required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = PaymentIntent.objects.get(
                reference=reference,
                client=request.user,
                status=PaymentIntentStatus.PENDING,
                payable_id__isnull=True,
            )
        except PaymentIntent.DoesNotExist:
            return Response({"cancelled": False, "detail": "Not found or already linked."}, status=status.HTTP_200_OK)

        PaymentIntentService.cancel_intent(payment_intent=intent)
        return Response({"cancelled": True}, status=status.HTTP_200_OK)


class MockPaymentConfirmView(APIView):
    """
    Dev/test only: instantly confirm a mock PaymentIntent.

    POSTing the reference of a pending mock intent marks it as succeeded
    and runs the same application logic that a real webhook would trigger
    (e.g. credits the wallet for wallet_top_up intents).

    Only works for intents where provider == "mock" and the intent belongs
    to the requesting user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from django.db import transaction

        reference = str(request.data.get("reference", "")).strip()
        if not reference:
            return Response({"detail": "reference required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = PaymentIntent.objects.select_for_update().get(
                reference=reference,
                client=request.user,
                provider="mock",
                status=PaymentIntentStatus.PENDING,
            )
        except PaymentIntent.DoesNotExist:
            return Response(
                {"detail": "Mock intent not found or already processed."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            intent.status = PaymentIntentStatus.SUCCEEDED
            intent.save(update_fields=["status", "updated_at"])

            result = PaymentApplicationService.apply_payment(
                payment_intent=intent,
                total_amount=intent.amount,
            )

        return Response({"confirmed": True, "result": result}, status=status.HTTP_200_OK)