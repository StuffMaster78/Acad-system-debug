from __future__ import annotations

from typing import Any

from django.db import IntegrityError, transaction
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


class WebhookProcessingService:
    """
    Handles provider webhook verification, deduplication, transaction recording,
    and payment intent state updates.
    """

    SUCCESS_STATUSES = {"successful", "success", "succeeded", "completed", "paid"}
    FAILED_STATUSES = {"failed", "error", "cancelled", "canceled"}
    PENDING_STATUSES = {"pending", "processing"}

    @classmethod
    def process_webhook(
        cls,
        *,
        provider_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process a webhook from a provider.

        Returns a normalized result describing what happened.
        """
        provider = get_provider(provider_key)

        is_verified = provider.verify_webhook(payload, headers)
        if not is_verified:
            raise PaymentVerificationError(
                f"Webhook verification failed for provider '{provider_key}'."
            )

        normalized_event = provider.parse_webhook(payload)

        event_id = str(normalized_event.get("event_id") or "")
        event_type = str(normalized_event.get("event_type") or "")
        reference = str(normalized_event.get("reference") or "")
        raw_status = str(normalized_event.get("status") or "").lower().strip()

        if not event_id:
            raise PaymentVerificationError(
                "Webhook event is missing a provider event ID."
            )

        if not reference:
            raise PaymentVerificationError(
                "Webhook event is missing a payment reference."
            )

        with transaction.atomic():
            webhook_event = cls._create_webhook_event(
                provider=provider_key,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                signature_verified=True,
            )

            payment_intent = get_payment_intent_by_reference(reference)
            if payment_intent is None:
                cls._mark_webhook_failed(
                    webhook_event=webhook_event,
                    error_message=(
                        f"No payment intent found for reference '{reference}'."
                    ),
                )
                raise PaymentIntentNotFoundError(
                    f"No payment intent found for reference '{reference}'."
                )

            transaction_kind = cls._resolve_transaction_kind(event_type=event_type)
            transaction_status = cls._resolve_transaction_status(raw_status=raw_status)
            payment_intent_status = cls._resolve_payment_intent_status(
                raw_status=raw_status,
                current_status=payment_intent.status,
            )

            PaymentTransactionService.create_transaction(
                payment_intent=payment_intent,
                provider=provider_key,
                kind=transaction_kind,
                status=transaction_status,
                amount=normalized_event.get("amount") or payment_intent.amount,
                currency=normalized_event.get("currency") or payment_intent.currency,
                provider_transaction_id=str(
                    normalized_event.get("provider_transaction_id") or ""
                ),
                provider_event_id=event_id,
                raw_payload=payload,
            )

            cls._update_payment_intent(
                payment_intent=payment_intent,
                new_status=payment_intent_status,
            )

            cls._mark_webhook_processed(webhook_event=webhook_event)

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
    ) -> ProviderWebhookEvent:
        """
        Create a webhook inbox record and block duplicates by unique constraint.
        """
        try:
            return ProviderWebhookEvent.objects.create(
                provider=provider,
                event_id=event_id,
                event_type=event_type,
                signature_verified=signature_verified,
                payload=payload,
                processing_status=WebhookProcessingStatus.RECEIVED,
            )
        except IntegrityError as exc:
            raise DuplicatePaymentEventError(
                f"Duplicate webhook event '{provider}:{event_id}' received."
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
        payment_intent,
        new_status: str,
    ) -> None:
        """
        Update payment intent status safely.
        """
        update_fields = ["status", "updated_at"]

        payment_intent.status = new_status

        if new_status == PaymentIntentStatus.SUCCEEDED:
            payment_intent.paid_at = timezone.now()
            update_fields.append("paid_at")

        payment_intent.save(update_fields=update_fields)