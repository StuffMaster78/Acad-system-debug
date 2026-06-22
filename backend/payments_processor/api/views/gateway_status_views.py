from __future__ import annotations

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


def _mask(value: str, visible: int = 8) -> str:
    """Return masked key — show first visible chars, rest as bullets."""
    if not value:
        return ""
    return value[:visible] + "•" * max(0, len(value) - visible)


def _key_mode(secret_key: str) -> str:
    if secret_key.startswith("sk_live_"):
        return "live"
    if secret_key.startswith("sk_test_"):
        return "test"
    return "unknown"


class PaymentGatewayStatusView(APIView):
    """
    Read-only summary of the current Stripe gateway configuration.

    Returns masked key prefixes so staff can confirm which credentials
    are loaded without ever exposing the raw secrets through the API.
    Keys are always read from environment variables — they must be
    changed there and the application restarted to take effect.
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request: Request) -> Response:
        secret_key: str = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
        publishable_key: str = getattr(settings, "STRIPE_PUBLISHABLE_KEY", "") or ""
        webhook_secret: str = getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or ""

        return Response(
            {
                "provider": "stripe",
                "mode": _key_mode(secret_key),
                "secret_key": {
                    "configured": bool(secret_key),
                    "masked": _mask(secret_key) if secret_key else None,
                },
                "publishable_key": {
                    "configured": bool(publishable_key),
                    "masked": _mask(publishable_key) if publishable_key else None,
                },
                "webhook_secret": {
                    "configured": bool(webhook_secret),
                    "masked": _mask(webhook_secret, 6) if webhook_secret else None,
                },
                "note": (
                    "Keys are loaded from environment variables. "
                    "Update STRIPE_SECRET_KEY / STRIPE_PUBLISHABLE_KEY / "
                    "STRIPE_WEBHOOK_SECRET and restart the application to apply changes."
                ),
            }
        )

    def post(self, request: Request) -> Response:
        """Test Stripe connectivity by listing payment methods (1 call, no charge)."""
        secret_key: str = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
        if not secret_key:
            return Response(
                {"success": False, "detail": "STRIPE_SECRET_KEY is not configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            import stripe
            stripe.api_key = secret_key
            stripe.PaymentMethod.list(type="card", limit=1)
            return Response({"success": True, "detail": "Stripe connection successful."})
        except Exception as exc:
            return Response(
                {"success": False, "detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
