from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentTransactionKind,
    PaymentTransactionStatus,
)
from payments_processor.exceptions import PaymentError, PaymentVerificationError
from payments_processor.models import PaymentIntent
from payments_processor.providers.registry import get_provider
from payments_processor.selectors.payment_transaction_selectors import (
    get_transaction_by_provider_transaction_id,
)
from payments_processor.services.payment_transaction_service import (
    PaymentTransactionService,
)


class PaymentVerificationService:
    """
    Verifies payment status directly with the provider and updates
    local records safely.
    """

    SUCCESS_STATUSES = {"successful", "success", "succeeded", "completed", "paid"}
    FAILED_STATUSES = {"failed", "error", "cancelled", "canceled"}
    PENDING_STATUSES = {"pending", "processing"}

    @classmethod
    @transaction.atomic
    def verify_payment_intent(
        cls,
        *,
        payment_intent: PaymentIntent,
        create_transaction: bool = True,
    ) -> dict[str, Any]:
        """
        Verify a payment intent directly with the provider.

        Returns:
            {
                "payment_intent": PaymentIntent,
                "verified_status": str,
                "transaction_status": str,
                "provider_data": dict,
                "requires_internal_application": bool,
            }
        """
        if not payment_intent.provider:
            raise PaymentVerificationError(
                "Payment intent has no provider configured."
            )

        provider_adapter = get_provider(payment_intent.provider)

        try:
            provider_response = provider_adapter.verify_payment(payment_intent)
        except Exception as exc:
            raise PaymentVerificationError(
                f"Provider verification failed for '{payment_intent.reference}'."
            ) from exc

        normalized = cls._normalize_provider_verification_response(
            payment_intent=payment_intent,
            provider_response=provider_response,
        )

        raw_status = normalized["status"]
        transaction_status = cls._resolve_transaction_status(raw_status=raw_status)
        payment_intent_status = cls._resolve_payment_intent_status(
            raw_status=raw_status,
            current_status=payment_intent.status,
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
    def _normalize_provider_verification_response(
        cls,
        *,
        payment_intent: PaymentIntent,
        provider_response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize provider verification response into a stable structure.
        """
        status = str(provider_response.get("status") or "").lower().strip()
        if not status:
            raise PaymentVerificationError(
                f"Provider verification returned no status for "
                f"'{payment_intent.reference}'."
            )

        amount = provider_response.get("amount", payment_intent.amount)
        currency = str(
            provider_response.get("currency") or payment_intent.currency
        ).upper()

        provider_transaction_id = str(
            provider_response.get("provider_transaction_id")
            or provider_response.get("transaction_id")
            or ""
        )

        provider_event_id = str(provider_response.get("provider_event_id") or "")
        reference = str(provider_response.get("reference") or payment_intent.reference)

        return {
            "status": status,
            "amount": amount,
            "currency": currency,
            "provider_transaction_id": provider_transaction_id,
            "provider_event_id": provider_event_id,
            "reference": reference,
            "raw_response": provider_response,
        }

    @classmethod
    def _record_verification_transaction_if_needed(
        cls,
        *,
        payment_intent: PaymentIntent,
        normalized: dict[str, Any],
        transaction_status: str,
    ) -> None:
        """
        Create a verification transaction record if one does not already exist
        for the provider transaction ID.
        """
        provider_transaction_id = normalized.get("provider_transaction_id") or ""
        provider_event_id = normalized.get("provider_event_id") or ""

        existing_transaction = None
        if provider_transaction_id:
            existing_transaction = get_transaction_by_provider_transaction_id(
                provider=payment_intent.provider,
                provider_transaction_id=provider_transaction_id,
            )

        if existing_transaction is not None:
            return

        PaymentTransactionService.create_transaction(
            payment_intent=payment_intent,
            provider=payment_intent.provider,
            kind=PaymentTransactionKind.CHARGE,
            status=transaction_status,
            amount=normalized["amount"],
            currency=normalized["currency"],
            provider_transaction_id=provider_transaction_id,
            provider_event_id=provider_event_id,
            raw_payload=normalized.get("raw_response") or {},
            occurred_at=timezone.now(),
        )

    @classmethod
    def _resolve_transaction_status(
        cls,
        *,
        raw_status: str,
    ) -> str:
        """
        Resolve normalized provider status into internal transaction status.
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
        Resolve normalized provider status into internal payment intent status.
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
        Update payment intent status safely.
        """
        if new_status == payment_intent.status:
            return

        update_fields = ["status", "updated_at"]
        payment_intent.status = new_status

        if (
            new_status == PaymentIntentStatus.SUCCEEDED
            and payment_intent.paid_at is None
        ):
            payment_intent.paid_at = timezone.now()
            update_fields.append("paid_at")

        payment_intent.save(update_fields=update_fields)