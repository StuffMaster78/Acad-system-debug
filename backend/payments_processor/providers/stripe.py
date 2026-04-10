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
from payments_processor.providers.exceptions import (
    PaymentProviderRefundError,
    PaymentProviderVerificationError,
    PaymentProviderWebhookError,
)
from payments_processor.providers.registry import register_provider


class StripePaymentProvider(BasePaymentProvider):
    provider_name = "stripe"

    def create_payment(
        self,
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        provider_reference = str(
            getattr(payment_intent, "provider_reference", "") or uuid4()
        )

        return ProviderCheckoutResult(
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            checkout_url="https://checkout.stripe.com/pay/example",
            client_secret="stripe_client_secret_placeholder",
            raw_response={
                "message": "Stripe checkout session created.",
            },
        )

    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        if payload is None:
            return ProviderWebhookVerificationResult(
                is_valid=False,
                error_message="Missing webhook payload.",
            )

        return ProviderWebhookVerificationResult(is_valid=True)

    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        if not payload:
            raise PaymentProviderWebhookError("Webhook payload is empty.")

        data_object = payload.get("data", {}).get("object", {})
        provider_reference = str(data_object.get("id", ""))
        amount = Decimal(str(data_object.get("amount_total", 0))) / Decimal("100")
        currency = str(data_object.get("currency", "usd")).upper()

        event_type = str(payload.get("type", "payment.updated"))
        if event_type in {
            "checkout.session.completed",
            "payment_intent.succeeded",
        }:
            status = "success"
        elif event_type in {
            "payment_intent.payment_failed",
            "charge.failed",
        }:
            status = "failed"
        else:
            status = "pending"

        return ProviderWebhookEvent(
            event_id=str(payload.get("id", uuid4())),
            event_type=event_type,
            status=status,
            amount=amount,
            currency=currency,
            provider_transaction_id=provider_reference,
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

        if refund_amount <= Decimal("0.00"):
            raise PaymentProviderRefundError("Refund amount must be positive.")

        return ProviderRefundResult(
            provider_name=self.provider_name,
            provider_reference=str(
                getattr(payment_intent, "provider_reference", "")
            ),
            refund_reference=str(uuid4()),
            status="success",
            amount=refund_amount,
            currency=str(getattr(payment_intent, "currency", "USD")),
            raw_response={
                "message": "Stripe refund created.",
            },
        )

    def verify_payment(
        self,
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        provider_reference = str(
            getattr(payment_intent, "provider_reference", "")
        )
        if not provider_reference:
            raise PaymentProviderVerificationError(
                "Payment intent has no provider reference."
            )

        return ProviderPaymentVerificationResult(
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            provider_transaction_id=str(
                getattr(payment_intent, "provider_transaction_id", "")
            ),
            status=str(getattr(payment_intent, "status", "pending")),
            amount=Decimal(str(getattr(payment_intent, "amount", "0.00"))),
            currency=str(getattr(payment_intent, "currency", "USD")),
            raw_response={
                "message": "Stripe verification stub response.",
            },
        )


register_provider(StripePaymentProvider)