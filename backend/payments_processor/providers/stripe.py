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
    """
    Stripe payment provider stub implementation.

    Replace placeholder URLs and response mapping with real Stripe SDK
    integration when wiring live provider calls.
    """

    provider_name = "stripe"

    def create_payment(
        self,
        payment_intent: Any,
    ) -> ProviderCheckoutResult:
        """
        Initialize a Stripe payment session.
        """
        provider_reference = str(
            getattr(payment_intent, "provider_reference", "") or uuid4()
        )

        return ProviderCheckoutResult(
            success=True,
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            checkout_url="https://checkout.stripe.com/pay/example",
            client_secret="stripe_client_secret_placeholder",
            status="pending",
            raw_response={
                "message": "Stripe checkout session created.",
            },
        )

    def verify_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> ProviderWebhookVerificationResult:
        """
        Verify Stripe webhook signature and payload presence.

        This is currently a stub. Replace with Stripe signature verification.
        """
        _ = headers

        if not payload:
            return ProviderWebhookVerificationResult(
                is_verified=False,
                error_message="Missing webhook payload.",
                raw_response={},
            )

        return ProviderWebhookVerificationResult(
            is_verified=True,
            error_message="",
            raw_response={},
        )

    def parse_webhook(
        self,
        payload: dict[str, Any],
    ) -> ProviderWebhookEvent:
        """
        Normalize a Stripe webhook payload.
        """
        if not payload:
            raise PaymentProviderWebhookError("Webhook payload is empty.")

        data_object = payload.get("data", {}).get("object", {})

        provider_transaction_id = str(data_object.get("id", "") or "")
        reference = str(
            data_object.get("client_reference_id")
            or data_object.get("metadata", {}).get("reference")
            or ""
        )

        amount_total = data_object.get("amount_total")
        amount: Decimal | None
        if amount_total is None:
            amount = None
        else:
            amount = Decimal(str(amount_total)) / Decimal("100")

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
            reference=reference,
            amount=amount,
            currency=currency,
            provider_transaction_id=provider_transaction_id,
            provider_event_id=str(payload.get("id", "") or ""),
            raw_payload=payload,
        )

    def refund_payment(
        self,
        payment_intent: Any,
        *,
        amount: Decimal | None = None,
    ) -> ProviderRefundResult:
        """
        Execute a Stripe refund.
        """
        refund_amount = amount or Decimal(
            str(getattr(payment_intent, "amount", "0.00"))
        )

        if refund_amount <= Decimal("0.00"):
            raise PaymentProviderRefundError(
                "Refund amount must be positive."
            )

        return ProviderRefundResult(
            success=True,
            status="success",
            amount=refund_amount,
            currency=str(getattr(payment_intent, "currency", "USD")),
            provider_name=self.provider_name,
            provider_refund_id=str(uuid4()),
            provider_transaction_id=str(
                getattr(payment_intent, "provider_transaction_id", "")
            ),
            reference=str(getattr(payment_intent, "reference", "")),
            raw_response={
                "message": "Stripe refund created.",
            },
            error_message="",
        )

    def verify_payment(
        self,
        payment_intent: Any,
    ) -> ProviderPaymentVerificationResult:
        """
        Verify payment status directly with Stripe.
        """
        provider_reference = str(
            getattr(payment_intent, "provider_reference", "")
        )
        if not provider_reference:
            raise PaymentProviderVerificationError(
                "Payment intent has no provider reference."
            )

        return ProviderPaymentVerificationResult(
            success=True,
            status=str(getattr(payment_intent, "status", "pending")),
            amount=Decimal(str(getattr(payment_intent, "amount", "0.00"))),
            currency=str(getattr(payment_intent, "currency", "USD")),
            provider_name=self.provider_name,
            provider_reference=provider_reference,
            provider_transaction_id=str(
                getattr(payment_intent, "provider_transaction_id", "")
            ),
            provider_event_id="",
            reference=str(getattr(payment_intent, "reference", "")),
            raw_response={
                "message": "Stripe verification stub response.",
            },
            error_message="",
        )


register_provider(StripePaymentProvider)