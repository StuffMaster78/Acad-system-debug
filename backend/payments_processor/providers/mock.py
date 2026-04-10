from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import uuid4

from payments_processor.providers.base import (
    BasePaymentProvider,
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderRefundResult,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)
from payments_processor.providers.registry import register_provider


class MockPaymentProvider(BasePaymentProvider):
    provider_name = "mock"

    def create_payment(
        self,
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        reference = getattr(payment_intent, "provider_reference", None) or str(uuid4())

        return ProviderCheckoutResult(
            provider_name=self.provider_name,
            provider_reference=reference,
            checkout_url="https://example.com/mock-checkout",
            raw_response={
                "message": "Mock payment initialized successfully.",
            },
        )

    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        return ProviderWebhookVerificationResult(
            is_valid=True,
        )

    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        amount_value = payload.get("amount", "0.00")
        currency = str(payload.get("currency", "USD"))
        provider_reference = str(payload.get("reference", ""))
        provider_transaction_id = str(
            payload.get("provider_transaction_id", provider_reference)
        )

        return ProviderWebhookEvent(
            event_id=str(payload.get("event_id", uuid4())),
            event_type=str(payload.get("event_type", "payment.updated")),
            status=str(payload.get("status", "success")),
            amount=Decimal(str(amount_value)),
            currency=currency,
            provider_transaction_id=provider_transaction_id,
            provider_reference=provider_reference,
            raw_payload=payload,
        )

    def refund_payment(
        self,
        payment_intent: Any,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        refund_amount = amount or Decimal(
            str(getattr(payment_intent, "amount", "0.00"))
        )
        currency = str(getattr(payment_intent, "currency", "USD"))
        provider_reference = str(
            getattr(payment_intent, "provider_reference", "")
        )

        return ProviderRefundResult(
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            refund_reference=str(uuid4()),
            status="success",
            amount=refund_amount,
            currency=currency,
            raw_response={
                "message": "Mock refund completed successfully.",
            },
        )

    def verify_payment(
        self,
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        return ProviderPaymentVerificationResult(
            provider_name=self.provider_name,
            provider_reference=str(
                getattr(payment_intent, "provider_reference", "")
            ),
            provider_transaction_id=str(
                getattr(payment_intent, "provider_transaction_id", "")
            ),
            status=str(getattr(payment_intent, "status", "success")),
            amount=Decimal(str(getattr(payment_intent, "amount", "0.00"))),
            currency=str(getattr(payment_intent, "currency", "USD")),
            raw_response={
                "message": "Mock verification completed successfully.",
            },
        )


register_provider(MockPaymentProvider)