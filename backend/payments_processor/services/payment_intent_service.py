from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from payments_processor.constants import (
    DEFAULT_CURRENCY,
    PAYMENT_INTENT_EXPIRY_MINUTES,
)
from payments_processor.enums import PaymentIntentStatus
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentIntent
from payments_processor.providers.registry import get_provider
from payments_processor.utils.references import generate_payment_reference


class PaymentIntentService:
    """
    Handles creation and initialization of payment intents.
    """

    @staticmethod
    @transaction.atomic
    def create_intent(
        *,
        customer,
        provider: str,
        purpose: str,
        amount,
        currency: str = DEFAULT_CURRENCY,
        payable=None,
        metadata: dict[str, Any] | None = None,
        reference_prefix: str = "pay",
    ) -> dict[str, Any]:
        """
        Create a payment intent and initialize it with the provider.

        Returns:
            {
                "payment_intent": PaymentIntent,
                "provider_data": dict,
            }
        """
        if amount is None or amount <= 0:
            raise PaymentError("Payment amount must be greater than zero.")

        reference = generate_payment_reference(prefix=reference_prefix)
        expires_at = timezone.now() + timedelta(
            minutes=PAYMENT_INTENT_EXPIRY_MINUTES
        )

        payment_intent = PaymentIntent.objects.create(
            reference=reference,
            customer=customer,
            purpose=purpose,
            provider=provider,
            status=PaymentIntentStatus.CREATED,
            currency=currency,
            amount=amount,
            payable=payable,
            metadata=metadata or {},
            expires_at=expires_at,
        )

        provider_adapter = get_provider(provider)
        provider_response = provider_adapter.create_payment(payment_intent)

        provider_intent_id = str(
            provider_response.get("provider_intent_id") or ""
        )

        payment_intent.provider_intent_id = provider_intent_id
        payment_intent.status = PaymentIntentStatus.PENDING
        payment_intent.save(
            update_fields=[
                "provider_intent_id",
                "status",
                "updated_at",
            ]
        )

        return {
            "payment_intent": payment_intent,
            "provider_data": provider_response,
        }

    @staticmethod
    def expire_intent(*, payment_intent: PaymentIntent) -> PaymentIntent:
        """
        Mark a payment intent as expired.
        """
        if payment_intent.status in {
            PaymentIntentStatus.SUCCEEDED,
            PaymentIntentStatus.REFUNDED,
            PaymentIntentStatus.PARTIALLY_REFUNDED,
        }:
            raise PaymentError(
                "Cannot expire a completed or refunded payment intent."
            )

        payment_intent.status = PaymentIntentStatus.EXPIRED
        payment_intent.save(update_fields=["status", "updated_at"])
        return payment_intent

    @staticmethod
    def cancel_intent(*, payment_intent: PaymentIntent) -> PaymentIntent:
        """
        Mark a payment intent as canceled.
        """
        if payment_intent.status == PaymentIntentStatus.SUCCEEDED:
            raise PaymentError("Cannot cancel a successful payment intent.")

        payment_intent.status = PaymentIntentStatus.CANCELED
        payment_intent.save(update_fields=["status", "updated_at"])
        return payment_intent