from __future__ import annotations

from decimal import Decimal
from typing import Any, TypedDict, cast

from django.db import transaction as db_transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentTransactionKind,
    PaymentTransactionStatus,
)
from payments_processor.exceptions import PaymentVerificationError
from payments_processor.models import PaymentIntent
from payments_processor.providers.registry import get_provider
from payments_processor.selectors.payment_transaction_selectors import (
    get_transaction_by_provider_transaction_id,
)
from payments_processor.services.payment_transaction_service import (
    PaymentTransactionService,
)
from payments_processor.tasks.payment_application_tasks import (
    apply_payment_intent_task,
)
from payments_processor.validators.webhook_validators import (
    validate_webhook_status_transition,
)


class VerificationResponse(TypedDict):
    """
    Normalized provider verification payload.
    """

    status: str
    amount: Decimal
    currency: str
    provider_transaction_id: str
    provider_event_id: str
    reference: str
    raw_response: dict[str, Any]


class PaymentVerificationService:
    """
    Verify payment status directly with the provider and update local
    records safely.
    """

    SUCCESS_STATUSES = {
        "successful",
        "success",
        "succeeded",
        "completed",
        "paid",
    }
    FAILED_STATUSES = {
        "failed",
        "error",
        "cancelled",
        "canceled",
    }
    PENDING_STATUSES = {
        "pending",
        "processing",
    }

    @classmethod
    @db_transaction.atomic
    def verify_payment_intent(
        cls,
        *,
        payment_intent: PaymentIntent,
        create_transaction: bool = True,
    ) -> dict[str, Any]:
        """
        Verify a payment intent directly with the provider and enqueue
        internal application on success.
        """
        provider_key = str(payment_intent.provider or "").strip()
        if not provider_key:
            raise PaymentVerificationError(
                "Payment intent has no provider configured."
            )

        provider_adapter = get_provider(provider_key)

        try:
            provider_response = provider_adapter.verify_payment(
                payment_intent
            )
        except Exception as exc:
            raise PaymentVerificationError(
                f"Provider verification failed for "
                f"'{payment_intent.reference}'."
            ) from exc

        normalized: VerificationResponse = {
            "status": provider_response.status.lower().strip(),
            "amount": provider_response.amount,
            "currency": provider_response.currency.upper(),
            "provider_transaction_id": provider_response.provider_transaction_id,
            "provider_event_id": provider_response.provider_event_id,
            "reference": provider_response.reference or payment_intent.reference,
            "raw_response": provider_response.raw_response,
        }

        raw_status = normalized["status"]
        transaction_status = cls._resolve_transaction_status(
            raw_status=raw_status,
        )
        payment_intent_status = cls._resolve_payment_intent_status(
            raw_status=raw_status,
            current_status=payment_intent.status,
        )

        validate_webhook_status_transition(
            current_status=payment_intent.status,
            new_status=payment_intent_status,
        )

        if create_transaction:
            cls._record_verification_transaction_if_needed(
                payment_intent=payment_intent,
                normalized=normalized,
                transaction_status=transaction_status,
            )

        cls._update_payment_intent(
            payment_intent=payment_intent,
            new_status=payment_intent_status,
        )

        if payment_intent.status == PaymentIntentStatus.SUCCEEDED:
            payment_task = cast(Any, apply_payment_intent_task)

            def enqueue_payment_application() -> None:
                payment_task.delay(payment_intent.pk)

            db_transaction.on_commit(enqueue_payment_application)

        return {
            "payment_intent": payment_intent,
            "verified_status": payment_intent.status,
            "transaction_status": transaction_status,
            "provider_data": normalized,
            "requires_internal_application": (
                payment_intent.status == PaymentIntentStatus.SUCCEEDED
            ),
        }


    @classmethod
    def _record_verification_transaction_if_needed(
        cls,
        *,
        payment_intent: PaymentIntent,
        normalized: VerificationResponse,
        transaction_status: str,
    ) -> None:
        """
        Create a verification transaction record if one does not already
        exist for the provider transaction ID.
        """
        provider_transaction_id = normalized["provider_transaction_id"]
        provider_event_id = normalized["provider_event_id"]

        existing_transaction = None
        if provider_transaction_id:
            existing_transaction = get_transaction_by_provider_transaction_id(
                provider=str(payment_intent.provider),
                provider_transaction_id=provider_transaction_id,
            )

        if existing_transaction is not None:
            return

        PaymentTransactionService.create_transaction(
            payment_intent=payment_intent,
            provider=str(payment_intent.provider),
            kind=PaymentTransactionKind.VERIFICATION,
            status=transaction_status,
            amount=normalized["amount"],
            currency=normalized["currency"],
            provider_transaction_id=provider_transaction_id,
            provider_event_id=provider_event_id,
            raw_payload=normalized["raw_response"],
            occurred_at=timezone.now(),
        )

    @classmethod
    def _resolve_transaction_status(
        cls,
        *,
        raw_status: str,
    ) -> str:
        """
        Resolve normalized provider status into internal transaction
        status.
        """
        if raw_status in cls.SUCCESS_STATUSES:
            return PaymentTransactionStatus.SUCCEEDED

        if raw_status in cls.FAILED_STATUSES:
            return PaymentTransactionStatus.FAILED

        if raw_status == "disputed":
            return PaymentTransactionStatus.DISPUTED

        if raw_status in cls.PENDING_STATUSES:
            return PaymentTransactionStatus.PENDING

        return PaymentTransactionStatus.PENDING

    @classmethod
    def _resolve_payment_intent_status(
        cls,
        *,
        raw_status: str,
        current_status: str,
    ) -> str:
        """
        Resolve normalized provider status into internal payment intent
        status.
        """
        if raw_status in cls.SUCCESS_STATUSES:
            return PaymentIntentStatus.SUCCEEDED

        if raw_status in cls.FAILED_STATUSES:
            return PaymentIntentStatus.FAILED

        if raw_status in cls.PENDING_STATUSES:
            return PaymentIntentStatus.PENDING

        return current_status

    @staticmethod
    def _update_payment_intent(
        *,
        payment_intent: PaymentIntent,
        new_status: str,
    ) -> None:
        """
        Update payment intent status and verification metadata safely.
        """
        update_fields = [
            "verification_attempts",
            "last_verified_at",
            "updated_at",
        ]

        payment_intent.verification_attempts += 1
        payment_intent.last_verified_at = timezone.now()

        if new_status != payment_intent.status:
            payment_intent.status = new_status
            update_fields.append("status")

            if (
                new_status == PaymentIntentStatus.SUCCEEDED
                and payment_intent.paid_at is None
            ):
                payment_intent.paid_at = timezone.now()
                update_fields.append("paid_at")

        payment_intent.save(update_fields=update_fields)