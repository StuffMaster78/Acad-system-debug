from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.models import PaymentIntent
from payments_processor.providers.base import (
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderRefundResult,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)
from payments_processor.providers.mapper import ProviderRequestAssembler
from payments_processor.providers.registry import get_provider


class PaymentProviderService:
    """
    Facade over payment providers.

    Accepts concrete PaymentIntent instances, builds provider request DTOs
    via ProviderRequestAssembler, and delegates to the selected provider.
    """

    @staticmethod
    def get_provider_for_intent(payment_intent: PaymentIntent):
        provider_name = str(payment_intent.provider or "").strip()
        if not provider_name:
            raise ValueError("Payment intent is missing provider.")
        return get_provider(provider_name)

    @staticmethod
    def create_payment(payment_intent: PaymentIntent) -> ProviderCheckoutResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        request = ProviderRequestAssembler.to_payment_request(payment_intent)
        return provider.create_payment(request)

    @staticmethod
    def verify_payment(payment_intent: PaymentIntent) -> ProviderPaymentVerificationResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        request = ProviderRequestAssembler.to_verification_request(payment_intent)
        return provider.verify_payment(request)

    @staticmethod
    def refund_payment(
        payment_intent: PaymentIntent,
        amount: Decimal,
    ) -> ProviderRefundResult:
        provider = PaymentProviderService.get_provider_for_intent(payment_intent)
        request = ProviderRequestAssembler.to_refund_request(payment_intent, amount)
        return provider.refund_payment(request)

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
