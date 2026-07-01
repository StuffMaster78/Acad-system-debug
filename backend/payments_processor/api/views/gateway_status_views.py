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

        platform_status = {
            "provider": "stripe",
            "scope": "platform_default",
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

        # Per-site config summary (superadmin only)
        per_site: list[dict] = []
        if getattr(request.user, "role", None) == "superadmin":
            from payments_processor.models.gateway_config import PaymentGatewayConfig
            for cfg in PaymentGatewayConfig.objects.select_related("website").order_by("website__name"):
                site_key = cfg.effective_secret_key
                site_whsec = cfg.effective_webhook_secret
                per_site.append({
                    "website": cfg.website.name,
                    "slug": cfg.website.slug,
                    "gateway": cfg.gateway,
                    "mode": cfg.mode,
                    "is_active": cfg.is_active,
                    "statement_descriptor": cfg.statement_descriptor or None,
                    "secret_key_env_var": cfg.secret_key_env_var or None,
                    "webhook_secret_env_var": cfg.webhook_secret_env_var or None,
                    "secret_key": {
                        "configured": bool(site_key),
                        "masked": _mask(site_key) if site_key else None,
                        "using_site_specific": bool(cfg.secret_key_env_var),
                    },
                    "webhook_secret": {
                        "configured": bool(site_whsec),
                        "masked": _mask(site_whsec, 6) if site_whsec else None,
                        "using_site_specific": bool(cfg.webhook_secret_env_var),
                    },
                    "webhook_url": f"/api/payments/webhooks/{cfg.gateway}/{cfg.website.slug}/",
                })
            platform_status["per_site"] = per_site

        return Response(platform_status)

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
