from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentRefundStatus,
    RefundDestination,
)
from payments_processor.exceptions import PaymentError, RefundExecutionError
from payments_processor.models import PaymentIntent, PaymentRefund
from payments_processor.providers.registry import get_provider


class RefundExecutionService:
    """
    Executes refunds through external payment providers and records
    payment-side refund execution history.
    """

    @classmethod
    @transaction.atomic
    def execute_refund(
        cls,
        *,
        payment_intent: PaymentIntent,
        amount: Decimal,
        destination: str = RefundDestination.ORIGINAL_METHOD,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a refund through the provider and create a PaymentRefund record.

        This service is for provider-side refund execution only.
        It does not apply internal refund side effects.
        """
        metadata = metadata or {}

        cls._validate_refund_request(
            payment_intent=payment_intent,
            amount=amount,
            destination=destination,
        )

        refund = PaymentRefund.objects.create(
            payment_intent=payment_intent,
            provider=payment_intent.provider,
            destination=destination,
            status=PaymentRefundStatus.REQUESTED,
            amount=amount,
            currency=payment_intent.currency,
            metadata=metadata,
        )

        provider_adapter = get_provider(payment_intent.provider)

        try:
            provider_response = provider_adapter.refund_payment(
                payment_intent,
                amount=amount,
            )
        except Exception as exc:
            refund.status = PaymentRefundStatus.FAILED
            refund.failure_message = str(exc)
            refund.processed_at = timezone.now()
            refund.save(
                update_fields=[
                    "status",
                    "failure_message",
                    "processed_at",
                ]
            )
            raise RefundExecutionError(
                f"Refund execution failed for payment "
                f"'{payment_intent.reference}'."
            ) from exc

        cls._apply_provider_refund_response(
            refund=refund,
            payment_intent=payment_intent,
            provider_response=provider_response,
        )

        return {
            "refund": refund,
            "provider_data": provider_response,
        }

    @staticmethod
    def _validate_refund_request(
        *,
        payment_intent: PaymentIntent,
        amount: Decimal,
        destination: str,
    ) -> None:
        """
        Validate whether the refund request is allowed.
        """
        if payment_intent.status not in {
            PaymentIntentStatus.SUCCEEDED,
            PaymentIntentStatus.PARTIALLY_REFUNDED,
        }:
            raise PaymentError(
                f"Payment '{payment_intent.reference}' is not refundable "
                f"from status '{payment_intent.status}'."
            )

        if amount <= Decimal("0.00"):
            raise PaymentError("Refund amount must be greater than zero.")

        refundable_amount = payment_intent.amount - payment_intent.amount_refunded
        if amount > refundable_amount:
            raise PaymentError(
                f"Refund amount exceeds refundable balance for payment "
                f"'{payment_intent.reference}'."
            )

        if destination not in RefundDestination.values:
            raise PaymentError(
                f"Unsupported refund destination '{destination}'."
            )

    @classmethod
    def _apply_provider_refund_response(
        cls,
        *,
        refund: PaymentRefund,
        payment_intent: PaymentIntent,
        provider_response: dict[str, Any],
    ) -> None:
        """
        Apply provider refund response to local payment refund state.
        """
        status = str(provider_response.get("status") or "").lower().strip()
        provider_refund_id = str(
            provider_response.get("provider_refund_id")
            or provider_response.get("refund_id")
            or ""
        )

        refund.provider_refund_id = provider_refund_id
        refund.raw_payload = provider_response

        if status in {"succeeded", "success", "completed"}:
            refund.status = PaymentRefundStatus.SUCCEEDED
            refund.processed_at = timezone.now()
            refund.save(
                update_fields=[
                    "provider_refund_id",
                    "raw_payload",
                    "status",
                    "processed_at",
                ]
            )

            cls._update_payment_intent_refund_state(
                payment_intent=payment_intent,
                refund_amount=refund.amount,
            )
            return

        if status in {"pending", "processing"}:
            refund.status = PaymentRefundStatus.PENDING
            refund.processed_at = timezone.now()
            refund.save(
                update_fields=[
                    "provider_refund_id",
                    "raw_payload",
                    "status",
                    "processed_at",
                ]
            )
            return

        refund.status = PaymentRefundStatus.FAILED
        refund.failure_message = str(
            provider_response.get("failure_message")
            or provider_response.get("message")
            or "Refund execution failed."
        )
        refund.processed_at = timezone.now()
        refund.save(
            update_fields=[
                "provider_refund_id",
                "raw_payload",
                "status",
                "failure_message",
                "processed_at",
            ]
        )

    @staticmethod
    def _update_payment_intent_refund_state(
        *,
        payment_intent: PaymentIntent,
        refund_amount: Decimal,
    ) -> None:
        """
        Update payment intent aggregate refund state after successful refund.
        """
        payment_intent.amount_refunded += refund_amount

        if payment_intent.amount_refunded >= payment_intent.amount:
            payment_intent.status = PaymentIntentStatus.REFUNDED
        else:
            payment_intent.status = PaymentIntentStatus.PARTIALLY_REFUNDED

        payment_intent.save(
            update_fields=[
                "amount_refunded",
                "status",
                "updated_at",
            ]
        )