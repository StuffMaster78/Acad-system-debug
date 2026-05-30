from __future__ import annotations

import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments_processor.enums import RefundDestination
from payments_processor.exceptions import (
    PaymentError,
    RefundExecutionError,
)
from payments_processor.models import PaymentIntent
from payments_processor.services.refund_execution_service import (
    RefundExecutionService,
)

log = logging.getLogger(__name__)


class InitiateRefundView(APIView):
    """
    Initiate a provider-side refund for a settled payment intent.

    POST /api/payments/refunds/
    {
        "payment_intent_id": 123,
        "amount": "50.00",           // optional — defaults to full amount
        "destination": "wallet"      // "wallet" | "original_method"
    }

    Staff / admin only. Validates the intent exists and is refundable,
    then calls RefundExecutionService which runs the provider refund and
    queues the internal application task.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not (
            getattr(request.user, "is_staff", False)
            or getattr(request.user, "is_superuser", False)
            or getattr(request.user, "is_admin", False)
        ):
            return Response(
                {"error": "Staff access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payment_intent_id = request.data.get("payment_intent_id")
        if not payment_intent_id:
            return Response(
                {"error": "payment_intent_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_amount = request.data.get("amount")
        destination = str(
            request.data.get("destination", RefundDestination.ORIGINAL_METHOD)
        )

        try:
            payment_intent = PaymentIntent.objects.select_related(
                "website"
            ).get(pk=payment_intent_id)
        except PaymentIntent.DoesNotExist:
            return Response(
                {"error": f"Payment intent {payment_intent_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Tenant check — requester must belong to the same website.
        requester_website_id = getattr(request.user, "website_id", None)
        if (
            requester_website_id is not None
            and requester_website_id != payment_intent.website_id
        ):
            return Response(
                {"error": "Cross-tenant refund not allowed."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if raw_amount is not None:
            try:
                amount = Decimal(str(raw_amount))
            except Exception:
                return Response(
                    {"error": "Invalid refund amount."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            amount = payment_intent.refundable_amount

        try:
            result = RefundExecutionService.execute_refund(
                payment_intent=payment_intent,
                amount=amount,
                destination=destination,
                metadata={"initiated_by": request.user.pk},
            )
            return Response(
                {
                    "refund_id": result["refund"].pk,
                    "amount": str(amount),
                    "destination": destination,
                    "idempotent": result.get("idempotent", False),
                    "status": result["refund"].status,
                },
                status=status.HTTP_201_CREATED,
            )

        except RefundExecutionError as exc:
            log.warning(
                "Refund execution failed intent=%s: %s", payment_intent_id, exc
            )
            return Response(
                {"error": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        except PaymentError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as exc:
            log.exception(
                "Unexpected refund error intent=%s: %s", payment_intent_id, exc
            )
            return Response(
                {"error": "Refund processing failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
