from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import IntegrityError, transaction as db_transaction
from django.utils import timezone

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentTransactionKind,
    PaymentTransactionStatus,
    WebhookProcessingStatus,
)
from payments_processor.exceptions import (
    DuplicatePaymentEventError,
    PaymentIntentNotFoundError,
    PaymentVerificationError,
)
from payments_processor.models import ProviderWebhookEvent
from payments_processor.providers.registry import get_provider
from payments_processor.selectors.payment_intent_selectors import (
    get_payment_intent_by_reference,
)
from payments_processor.services.payment_transaction_service import (
    PaymentTransactionService,
)
from payments_processor.tasks.payment_application_tasks import (
    apply_payment_intent_task,
)
from payments_processor.validators.webhook_validators import (
    validate_signature_verified,
    validate_webhook_event_id,
    validate_webhook_event_type,
    validate_webhook_payload,
    validate_webhook_provider,
    validate_webhook_status_transition,
)


class WebhookProcessingService:
    """
    Handle provider webhook verification, deduplication, transaction
    recording, and payment intent state updates.
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
    def process_webhook(
        cls,
        *,
        provider_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a webhook from a provider and enqueue internal payment
        application on success.
        """
        validate_webhook_provider(provider_key)
        validate_webhook_payload(payload)

        provider = get_provider(provider_key)

        verification_result = provider.verify_webhook(payload, headers)
        validate_signature_verified(verification_result.is_verified)

        normalized_event = provider.parse_webhook(payload)

        event_id = normalized_event.event_id
        event_type = normalized_event.event_type
        reference = normalized_event.reference
        raw_status = normalized_event.status.lower().strip()

        validate_webhook_event_id(event_id)
        validate_webhook_event_type(event_type)

        if not reference:
            raise PaymentVerificationError(
                "Webhook event is missing a payment reference."
            )

        with db_transaction.atomic():
            payment_intent = get_payment_intent_by_reference(reference)
            if payment_intent is None:
                webhook_event = cls._create_webhook_event(
                    provider=provider_key,
                    event_id=event_id,
                    event_type=event_type,
                    payload=payload,
                    signature_verified=True,
                )
                cls._mark_webhook_failed(
                    webhook_event=webhook_event,
                    error_message=(
                        f"No payment intent found for reference "
                        f"'{reference}'."
                    ),
                )
                raise PaymentIntentNotFoundError(
                    f"No payment intent found for reference '{reference}'."
                )

            webhook_event = cls._create_webhook_event(
                provider=provider_key,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                signature_verified=True,
                payment_intent=payment_intent,
            )

            transaction_kind = cls._resolve_transaction_kind(
                event_type=event_type,
            )
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

            amount = normalized_event.amount or payment_intent.amount
            currency = (
                normalized_event.currency or payment_intent.currency
            ).upper()

            PaymentTransactionService.create_transaction(
                payment_intent=payment_intent,
                provider=provider_key,
                kind=transaction_kind,
                status=transaction_status,
                amount=amount,
                currency=currency,
                provider_transaction_id=(
                    normalized_event.provider_transaction_id
                ),
                provider_event_id=event_id,
                raw_payload=payload,
            )

            cls._update_payment_intent(
                payment_intent=payment_intent,
                new_status=payment_intent_status,
            )

            cls._mark_webhook_processed(webhook_event=webhook_event)

            if payment_intent.status == PaymentIntentStatus.SUCCEEDED:
                payment_task = cast(Any, apply_payment_intent_task)

                def enqueue_payment_application() -> None:
                    payment_task.delay(payment_intent.pk)

                db_transaction.on_commit(enqueue_payment_application)

        return {
            "provider": provider_key,
            "event_id": event_id,
            "event_type": event_type,
            "reference": reference,
            "payment_intent_id": payment_intent.pk,
            "payment_intent_status": payment_intent.status,
            "transaction_status": transaction_status,
            "requires_internal_application": (
                payment_intent.status == PaymentIntentStatus.SUCCEEDED
            ),
        }

    @staticmethod
    def _create_webhook_event(
        *,
        provider: str,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        signature_verified: bool,
        payment_intent: Any | None = None,
    ) -> ProviderWebhookEvent:
        """
        Create a webhook inbox record and block duplicates by unique
        constraint.
        """
        create_kwargs: dict[str, Any] = {
            "provider": provider,
            "event_id": event_id,
            "event_type": event_type,
            "signature_verified": signature_verified,
            "payload": payload,
            "processing_status": WebhookProcessingStatus.RECEIVED,
        }

        if payment_intent is not None:
            create_kwargs["payment_intent"] = payment_intent
            if hasattr(payment_intent, "website"):
                create_kwargs["website"] = payment_intent.website

        try:
            return ProviderWebhookEvent.objects.create(**create_kwargs)
        except IntegrityError as exc:
            raise DuplicatePaymentEventError(
                f"Duplicate webhook event '{provider}:{event_id}' "
                f"received."
            ) from exc

    @staticmethod
    def _mark_webhook_processed(
        *,
        webhook_event: ProviderWebhookEvent,
    ) -> None:
        """
        Mark webhook event as successfully processed.
        """
        webhook_event.processing_status = WebhookProcessingStatus.PROCESSED
        webhook_event.error_message = ""
        webhook_event.processed_at = timezone.now()
        webhook_event.save(
            update_fields=[
                "processing_status",
                "error_message",
                "processed_at",
            ]
        )

    @staticmethod
    def _mark_webhook_failed(
        *,
        webhook_event: ProviderWebhookEvent,
        error_message: str,
    ) -> None:
        """
        Mark webhook event as failed.
        """
        webhook_event.processing_status = WebhookProcessingStatus.FAILED
        webhook_event.error_message = error_message
        webhook_event.processed_at = timezone.now()
        webhook_event.save(
            update_fields=[
                "processing_status",
                "error_message",
                "processed_at",
            ]
        )

    @classmethod
    def _resolve_transaction_kind(
        cls,
        *,
        event_type: str,
    ) -> str:
        """
        Resolve provider event type to internal transaction kind.
        """
        normalized = event_type.lower().strip()

        if "refund" in normalized:
            return PaymentTransactionKind.REFUND

        if "chargeback" in normalized or "dispute" in normalized:
            return PaymentTransactionKind.CHARGEBACK

        if "authorize" in normalized or "authorization" in normalized:
            return PaymentTransactionKind.AUTHORIZATION

        if "capture" in normalized:
            return PaymentTransactionKind.CAPTURE

        return PaymentTransactionKind.CHARGE

    @classmethod
    def _resolve_transaction_status(
        cls,
        *,
        raw_status: str,
    ) -> str:
        """
        Resolve provider status to internal transaction status.
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
        Resolve provider status to internal payment intent status.
        """
        if raw_status in cls.SUCCESS_STATUSES:
            return PaymentIntentStatus.SUCCEEDED

        if raw_status in cls.FAILED_STATUSES:
            return PaymentIntentStatus.FAILED

        if raw_status in cls.PENDING_STATUSES:
            if current_status == PaymentIntentStatus.REQUIRES_ACTION:
                return current_status
            return PaymentIntentStatus.PENDING

        return current_status

    @staticmethod
    def _update_payment_intent(
        *,
        payment_intent: Any,
        new_status: str,
    ) -> None:
        """
        Update payment intent status safely.
        """
        update_fields = ["updated_at"]

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