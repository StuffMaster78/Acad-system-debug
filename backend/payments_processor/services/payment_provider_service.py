from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.providers.registry import get_provider
from payments_processor.providers.base import (
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderRefundResult,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)


class PaymentProviderService:
    """
    Facade over payment providers.

    This keeps provider lookup and provider interaction out of views,
    models, and unrelated services.
    """

    @staticmethod
    def get_provider_for_intent(payment_intent: Any):
        """
        Resolve provider adapter for a payment intent.

        Supports both `provider` and legacy `provider_name` attributes.
        """
        provider_name = str(
            getattr(payment_intent, "provider", "")
            or getattr(payment_intent, "provider_name", "")
            or ""
        ).strip()

        if not provider_name:
            raise ValueError("Payment intent is missing provider.")

        return get_provider(provider_name)

    @staticmethod
    def create_payment(
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        """
        Initialize provider-side payment.
        """
        provider = PaymentProviderService.get_provider_for_intent(
            payment_intent
        )
        return provider.create_payment(payment_intent)

    @staticmethod
    def verify_payment(
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        """
        Verify payment directly with the provider.
        """
        provider = PaymentProviderService.get_provider_for_intent(
            payment_intent
        )
        return provider.verify_payment(payment_intent)

    @staticmethod
    def refund_payment(
        payment_intent: Any,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        """
        Execute provider-side refund.
        """
        provider = PaymentProviderService.get_provider_for_intent(
            payment_intent
        )
        return provider.refund_payment(
            payment_intent,
            amount=amount,
        )

    @staticmethod
    def verify_webhook(
        *,
        provider_name: str,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        """
        Verify webhook signature and authenticity.
        """
        provider = get_provider(provider_name)
        return provider.verify_webhook(payload, headers)

    @staticmethod
    def parse_webhook(
        *,
        provider_name: str,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        """
        Parse raw webhook payload into normalized provider event.
        """
        provider = get_provider(provider_name)
        return provider.parse_webhook(payload)