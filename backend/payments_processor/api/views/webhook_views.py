from __future__ import annotations

import json
import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from payments_processor.exceptions import (
    DuplicatePaymentEventError,
    PaymentIntentNotFoundError,
    PaymentVerificationError,
)
from payments_processor.services.webhook_processing_service import (
    WebhookProcessingService,
)

log = logging.getLogger(__name__)


class PaymentWebhookView(APIView):
    """
    Receive and process payment provider webhooks.

    URL pattern: POST /api/payments/webhooks/<provider>/
    where <provider> is the registered provider key (e.g. "stripe").

    No authentication — provider identity is verified via signature.
    Returns 200 for all processed events (including ignored ones) to
    prevent the provider from retrying on business-logic errors.
    Returns 400 only for malformed payloads or unregistered providers.
    Returns 500 on transient errors so the provider retries.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider: str, *args, **kwargs):
        provider_key = provider.lower().strip()

        try:
            if request.content_type and "json" in request.content_type:
                payload = request.data
            else:
                payload = json.loads(request.body or "{}")
        except (json.JSONDecodeError, ValueError) as exc:
            log.warning(
                "Webhook payload parse error provider=%s: %s", provider_key, exc
            )
            return Response(
                {"error": "Invalid payload format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            k: v for k, v in request.META.items() if k.startswith("HTTP_")
        }

        try:
            result = WebhookProcessingService.process_webhook(
                provider_key=provider_key,
                payload=payload,
                headers=headers,
            )
            return Response(
                {"received": True, **result}, status=status.HTTP_200_OK
            )

        except DuplicatePaymentEventError:
            return Response(
                {"received": True, "duplicate": True},
                status=status.HTTP_200_OK,
            )

        except PaymentIntentNotFoundError as exc:
            log.warning(
                "Webhook: intent not found provider=%s: %s", provider_key, exc
            )
            return Response(
                {"received": True, "skipped": True}, status=status.HTTP_200_OK
            )

        except PaymentVerificationError as exc:
            log.warning(
                "Webhook signature verification failed provider=%s: %s",
                provider_key,
                exc,
            )
            return Response(
                {"error": "Signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            log.warning(
                "Webhook validation error provider=%s: %s", provider_key, exc
            )
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as exc:
            log.exception(
                "Webhook processing error provider=%s: %s", provider_key, exc
            )
            return Response(
                {"error": "Internal processing error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
