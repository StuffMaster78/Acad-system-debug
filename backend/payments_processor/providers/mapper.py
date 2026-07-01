from __future__ import annotations

from decimal import Decimal

from django.conf import settings

from payments_processor.models import PaymentIntent
from payments_processor.providers.base import (
    ProviderMetadata,
    ProviderPaymentRequest,
    ProviderRefundRequest,
    ProviderVerificationRequest,
)


class ProviderRequestAssembler:
    """
    Assembles provider-facing request DTOs from PaymentIntent domain objects.

    This is the single authoritative boundary between InfoQ's domain model
    and the external payment provider world. It is responsible for:

    - Selecting the correct product name from a closed catalog
    - Constructing InfoQ relay redirect URLs (providers never see merchant domains)
    - Building the frozen ProviderMetadata (the only keys that reach providers)
    - Mapping provider checkout and payment IDs into typed DTO fields
    - Failing fast when required provider references are missing

    Providers receive immutable DTOs and cannot inspect the domain model.
    """

    _PRODUCT_NAMES: dict[str, str] = {
        "order":                   "InfoQ Digital Service",
        "order_payment":           "InfoQ Digital Service",
        "special_order":           "InfoQ Professional Service",
        "special_order_payment":   "InfoQ Professional Service",
        "invoice":                 "InfoQ Professional Service",
        "billing_payment_request": "InfoQ Professional Service",
        "wallet_top_up":           "InfoQ Wallet Credit",
        "class_purchase":          "InfoQ Digital Service",
        "class_order_payment":     "InfoQ Digital Service",
        "bundle_purchase":         "InfoQ Digital Service",
        "tip":                     "InfoQ Digital Service",
        "extra_order_charge":      "InfoQ Digital Service",
        "manual_billing":          "InfoQ Professional Service",
    }
    _FALLBACK_PRODUCT = "InfoQ Digital Service"

    @classmethod
    def to_payment_request(cls, payment_intent: PaymentIntent) -> ProviderPaymentRequest:
        # Prefer gateway config callback URL → website.root_url → global fallback
        gateway_cfg = getattr(payment_intent.website, "payment_gateway_config", None)
        if gateway_cfg and gateway_cfg.is_active:
            infoq_base = gateway_cfg.effective_callback_base_url
        else:
            site_url = getattr(payment_intent.website, "root_url", None) or ""
            infoq_base = (site_url or getattr(settings, "INFOQ_PAYMENT_BASE_URL", "")).rstrip("/")
        ref = payment_intent.reference

        statement_descriptor = (
            gateway_cfg.statement_descriptor.strip()
            if gateway_cfg and gateway_cfg.is_active and gateway_cfg.statement_descriptor
            else ""
        )

        return ProviderPaymentRequest(
            merchant_reference=ref,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            product_name=cls._PRODUCT_NAMES.get(
                payment_intent.purpose, cls._FALLBACK_PRODUCT
            ),
            success_url=f"{infoq_base}/payment/complete?status=success&ref={ref}",
            cancel_url=f"{infoq_base}/payment/complete?status=cancelled&ref={ref}",
            customer_email=getattr(payment_intent.client, "email", "") or "",
            metadata=ProviderMetadata(
                merchant_reference=ref,
                environment=getattr(settings, "ENVIRONMENT", "production"),
            ),
            statement_descriptor=statement_descriptor,
        )

    @classmethod
    def to_refund_request(
        cls,
        payment_intent: PaymentIntent,
        amount: Decimal,
    ) -> ProviderRefundRequest:
        checkout_id = payment_intent.provider_intent_id or ""
        payment_id = payment_intent.provider_transaction_id or ""

        if not checkout_id and not payment_id:
            raise ValueError(
                f"Cannot assemble refund request for '{payment_intent.reference}': "
                "payment has no provider reference. "
                "Verify the intent has been processed by the provider."
            )

        return ProviderRefundRequest(
            merchant_reference=payment_intent.reference,
            amount=amount,
            currency=payment_intent.currency,
            provider_checkout_id=checkout_id,
            provider_payment_id=payment_id,
        )

    @classmethod
    def to_verification_request(
        cls,
        payment_intent: PaymentIntent,
    ) -> ProviderVerificationRequest:
        checkout_id = payment_intent.provider_intent_id or ""
        payment_id = payment_intent.provider_transaction_id or ""

        if not checkout_id and not payment_id:
            raise ValueError(
                f"Cannot assemble verification request for '{payment_intent.reference}': "
                "payment has no provider reference. "
                "Verify the intent has been initialized with a provider."
            )

        return ProviderVerificationRequest(
            merchant_reference=payment_intent.reference,
            provider_checkout_id=checkout_id,
            provider_payment_id=payment_id,
        )
