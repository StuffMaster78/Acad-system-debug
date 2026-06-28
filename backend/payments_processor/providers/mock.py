from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import uuid4

from payments_processor.providers.base import (
    BasePaymentProvider,
    ProviderCheckoutResult,
    ProviderPaymentVerificationResult,
    ProviderPaymentRequest,
    ProviderRefundRequest,
    ProviderRefundResult,
    ProviderVerificationRequest,
    ProviderWebhookEvent,
    ProviderWebhookVerificationResult,
)
from payments_processor.providers.registry import register_provider


class MockPaymentProvider(BasePaymentProvider):
    provider_name = "mock"

    def create_payment(
        self,
        request: ProviderPaymentRequest,
    ) -> ProviderCheckoutResult:
        return ProviderCheckoutResult(
            success=True,
            provider_name=self.provider_name,
            provider_reference=f"mock_{uuid4().hex[:16]}",
            checkout_url="https://example.com/mock-checkout",
            raw_response={"message": "Mock payment initialized successfully."},
        )

    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        return ProviderWebhookVerificationResult(is_verified=True)

    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        amount_value = payload.get("amount", "0.00")
        currency = str(payload.get("currency", "USD"))
        reference = str(payload.get("reference", ""))
        provider_transaction_id = str(
            payload.get("provider_transaction_id", reference)
        )

        return ProviderWebhookEvent(
            event_id=str(payload.get("event_id", uuid4())),
            event_type=str(payload.get("event_type", "payment.updated")),
            status=str(payload.get("status", "success")),
            amount=Decimal(str(amount_value)),
            currency=currency,
            reference=reference,
            provider_transaction_id=provider_transaction_id,
            provider_event_id=reference,
            raw_payload=payload,
        )

    def refund_payment(
        self,
        request: ProviderRefundRequest,
    ) -> ProviderRefundResult:
        return ProviderRefundResult(
            success=True,
            provider_name=self.provider_name,
            status="success",
            amount=request.amount,
            currency=request.currency,
            provider_refund_id=str(uuid4()),
            provider_transaction_id=request.provider_checkout_id,
            reference=request.merchant_reference,
            raw_response={"message": "Mock refund completed successfully."},
        )

    def verify_payment(
        self,
        request: ProviderVerificationRequest,
    ) -> ProviderPaymentVerificationResult:
        return ProviderPaymentVerificationResult(
            success=True,
            provider_name=self.provider_name,
            provider_reference=request.provider_checkout_id or request.provider_payment_id,
            provider_transaction_id=request.provider_payment_id,
            status="success",
            amount=Decimal("0.00"),
            currency="USD",
            raw_response={"message": "Mock verification completed successfully."},
        )


register_provider(MockPaymentProvider)
