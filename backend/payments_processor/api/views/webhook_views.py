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

    Two URL patterns are registered:

        POST /api/payments/webhooks/<provider>/
            Platform-wide endpoint — uses the global STRIPE_WEBHOOK_SECRET.

        POST /api/payments/webhooks/<provider>/<site_slug>/
            Per-site endpoint — looks up the Website by slug and uses that
            site's configured webhook secret (from its PaymentGatewayConfig).
            Register this URL in the Stripe dashboard for each site's separate
            Stripe account so that signature verification uses the right secret.

    No authentication — provider identity is verified via HMAC signature.
    Returns 200 for all processed events (including duplicates and skips) to
    prevent the provider from retrying on business-logic errors.
    Returns 400 for malformed payloads, unknown providers, or unknown site slugs.
    Returns 500 on transient errors so the provider retries.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider: str, site_slug: str = "", *args, **kwargs):
        provider_key = provider.lower().strip()

        try:
            if request.content_type and "json" in request.content_type:
                payload = request.data
            else:
                payload = json.loads(request.body or "{}")
        except (json.JSONDecodeError, ValueError) as exc:
            log.warning(
                "Webhook payload parse error provider=%s site=%s: %s",
                provider_key, site_slug or "global", exc,
            )
            return Response(
                {"error": "Invalid payload format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {k: v for k, v in request.META.items() if k.startswith("HTTP_")}
        headers["_raw_body"] = request.body

        # Resolve the website when a slug is present in the URL
        website = None
        if site_slug:
            from websites.models.websites import Website
            try:
                website = (
                    Website.objects
                    .select_related("payment_gateway_config")
                    .get(slug=site_slug.lower().strip())
                )
            except Website.DoesNotExist:
                log.warning(
                    "Webhook: unknown site_slug=%s provider=%s",
                    site_slug, provider_key,
                )
                return Response(
                    {"error": f"Unknown site: {site_slug!r}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            result = WebhookProcessingService.process_webhook(
                provider_key=provider_key,
                payload=payload,
                headers=headers,
                website=website,
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
                "Webhook: intent not found provider=%s site=%s: %s",
                provider_key, site_slug or "global", exc,
            )
            return Response(
                {"received": True, "skipped": True}, status=status.HTTP_200_OK
            )

        except PaymentVerificationError as exc:
            log.warning(
                "Webhook signature verification failed provider=%s site=%s: %s",
                provider_key, site_slug or "global", exc,
            )
            return Response(
                {"error": "Signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            log.warning(
                "Webhook validation error provider=%s site=%s: %s",
                provider_key, site_slug or "global", exc,
            )
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as exc:
            log.exception(
                "Webhook processing error provider=%s site=%s: %s",
                provider_key, site_slug or "global", exc,
            )
            return Response(
                {"error": "Internal processing error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
