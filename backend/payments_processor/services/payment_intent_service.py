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
    Handle creation and initialization of payment intents.

    This service creates a local payment intent record, initializes the
    checkout flow with the selected provider, persists provider
    identifiers, and returns both the local intent and provider checkout
    data.
    """

    @staticmethod
    @transaction.atomic
    def create_intent(
        *,
        client,
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

        Args:
            client:
                Client associated with the payment intent.
            provider:
                Provider key used to initialize checkout.
            purpose:
                Business purpose of the payment intent.
            amount:
                Amount to be collected.
            currency:
                Currency code for the payment.
            payable:
                Optional payable domain object linked to the payment.
            metadata:
                Optional structured metadata stored on the intent.
            reference_prefix:
                Prefix used when generating the payment reference.

        Returns:
            dict[str, Any]:
                A dictionary containing:
                    payment_intent:
                        The created local PaymentIntent instance.
                    provider_data:
                        The structured provider checkout result returned
                        by the provider adapter.

        Raises:
            PaymentError:
                Raised when the amount is invalid.
        """
        if amount is None or amount <= 0:
            raise PaymentError(
                "Payment amount must be greater than zero."
            )

        reference = generate_payment_reference(prefix=reference_prefix)
        expires_at = timezone.now() + timedelta(
            minutes=PAYMENT_INTENT_EXPIRY_MINUTES
        )

        payment_intent = PaymentIntent.objects.create(
            reference=reference,
            client=client,
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

        provider_intent_id = provider_response.provider_reference

        if not provider_intent_id:
            raise PaymentError(
                "Provider response missing provider_reference."
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

        Args:
            payment_intent:
                Payment intent instance to expire.

        Returns:
            PaymentIntent:
                Updated expired payment intent.

        Raises:
            PaymentError:
                Raised when the payment intent is already completed or
                refunded.
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

        Args:
            payment_intent:
                Payment intent instance to cancel.

        Returns:
            PaymentIntent:
                Updated canceled payment intent.

        Raises:
            PaymentError:
                Raised when the payment intent is already successful.
        """
        if payment_intent.status == PaymentIntentStatus.SUCCEEDED:
            raise PaymentError(
                "Cannot cancel a successful payment intent."
            )

        payment_intent.status = PaymentIntentStatus.CANCELED
        payment_intent.save(update_fields=["status", "updated_at"])
        return payment_intent