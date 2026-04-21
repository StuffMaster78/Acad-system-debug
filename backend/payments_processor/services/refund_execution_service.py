from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction as db_transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentRefundStatus,
    RefundDestination,
)
from payments_processor.exceptions import (
    PaymentError,
    RefundExecutionError,
)
from payments_processor.models import PaymentIntent, PaymentRefund
from payments_processor.providers.registry import get_provider
from payments_processor.tasks.refund_tasks import apply_refund_task


class RefundExecutionService:
    """
    Execute provider-side refunds and persist refund state.

    This service only handles external provider execution and local refund
    tracking. Internal wallet and ledger reversal is delegated to the
    refund application flow.
    """

    @classmethod
    @db_transaction.atomic
    def execute_refund(
        cls,
        *,
        payment_intent: PaymentIntent,
        amount: Decimal,
        destination: str = RefundDestination.ORIGINAL_METHOD,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a refund through the provider and persist refund state.
        """
        metadata = metadata or {}

        cls._validate_refund_request(
            payment_intent=payment_intent,
            amount=amount,
            destination=destination,
        )

        existing = PaymentRefund.objects.filter(
            payment_intent=payment_intent,
            amount=amount,
            status__in=[
                PaymentRefundStatus.SUCCEEDED,
                PaymentRefundStatus.PENDING,
            ],
        ).first()

        if existing is not None:
            return {
                "refund": existing,
                "provider_data": existing.raw_payload,
                "idempotent": True,
            }

        refund = PaymentRefund.objects.create(
            website=payment_intent.website,
            payment_intent=payment_intent,
            provider=str(payment_intent.provider),
            destination=destination,
            status=PaymentRefundStatus.REQUESTED,
            amount=amount,
            currency=payment_intent.currency,
            metadata=metadata,
        )

        provider = get_provider(str(payment_intent.provider))

        try:
            provider_response = provider.refund_payment(
                payment_intent,
                amount=amount,
            )
        except Exception as exc:
            cls._mark_refund_failed(
                refund=refund,
                message=str(exc),
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
                f"Payment '{payment_intent.reference}' is not refundable."
            )

        if amount <= Decimal("0.00"):
            raise PaymentError("Refund amount must be greater than zero.")

        refundable = payment_intent.amount - payment_intent.amount_refunded
        if amount > refundable:
            raise PaymentError(
                "Refund amount exceeds refundable balance."
            )

        valid_destinations = {
            choice[0] for choice in RefundDestination.choices
        }
        if destination not in valid_destinations:
            raise PaymentError(
                f"Unsupported refund destination '{destination}'."
            )

    @classmethod
    def _apply_provider_refund_response(
        cls,
        *,
        refund: PaymentRefund,
        payment_intent: PaymentIntent,
        provider_response: Any,
    ) -> None:
        """
        Apply provider refund response to local refund state.
        """
        status = str(
            getattr(provider_response, "status", "") or ""
        ).lower().strip()

        provider_refund_id = str(
            getattr(provider_response, "provider_refund_id", "")
            or getattr(provider_response, "refund_id", "")
            or ""
        ).strip()

        refund.provider_refund_id = provider_refund_id
        refund.raw_payload = cls._to_dict(provider_response)

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

            refund_task = cast(Any, apply_refund_task)

            def enqueue_refund_application() -> None:
                refund_task.delay(refund.pk)

            db_transaction.on_commit(enqueue_refund_application)
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

        cls._mark_refund_failed(
            refund=refund,
            message=str(
                getattr(provider_response, "failure_message", "")
                or getattr(provider_response, "message", "")
                or "Refund execution failed."
            ),
        )

    @staticmethod
    def _mark_refund_failed(
        *,
        refund: PaymentRefund,
        message: str,
    ) -> None:
        """
        Mark refund as failed.
        """
        refund.status = PaymentRefundStatus.FAILED
        refund.failure_message = message
        refund.processed_at = timezone.now()
        refund.save(
            update_fields=[
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
        Update aggregate refund state on the payment intent.
        """
        payment_intent.amount_refunded += refund_amount

        if payment_intent.amount_refunded >= payment_intent.amount:
            payment_intent.status = PaymentIntentStatus.REFUNDED
        else:
            payment_intent.status = (
                PaymentIntentStatus.PARTIALLY_REFUNDED
            )

        payment_intent.save(
            update_fields=[
                "amount_refunded",
                "status",
                "updated_at",
            ]
        )

    @staticmethod
    def _to_dict(source: Any) -> dict[str, Any]:
        """
        Convert provider response to a dictionary for persistence.
        """
        if isinstance(source, dict):
            return source

        return dict(vars(source))