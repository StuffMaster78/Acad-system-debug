from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.providers import get_provider
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
        provider_name = str(getattr(payment_intent, "provider_name", "")).strip()

        if not provider_name:
            raise ValueError("Payment intent is missing provider_name.")

        return get_provider(provider_name)

    @staticmethod
    def create_payment(payment_intent: Any) -> ProviderCheckoutResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        return provider.create_payment(payment_intent)

    @staticmethod
    def verify_payment(
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        return provider.verify_payment(payment_intent)

    @staticmethod
    def refund_payment(
        payment_intent: Any,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        return provider.refund_payment(payment_intent, amount=amount)

    @staticmethod
    def verify_webhook(
        *,
        provider_name: str,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        provider = get_provider(provider_name)
        return provider.verify_webhook(payload, headers)

    @staticmethod
    def parse_webhook(
        *,
        provider_name: str,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        provider = get_provider(provider_name)
        return provider.parse_webhook(payload)