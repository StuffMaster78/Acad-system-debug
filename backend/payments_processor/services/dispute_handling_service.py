from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from payments_processor.enums import PaymentDisputeStatus
from payments_processor.exceptions import PaymentError
from payments_processor.models import PaymentDispute, PaymentIntent, PaymentTransaction
from payments_processor.selectors.payment_dispute_selectors import (
    get_payment_dispute_by_provider_dispute_id,
)


class DisputeHandlingService:
    """
    Handles provider disputes, chargebacks, and reversals.
    """

    @classmethod
    @transaction.atomic
    def record_dispute(
        cls,
        *,
        payment_intent: PaymentIntent,
        provider: str,
        provider_dispute_id: str,
        amount: Decimal,
        currency: str,
        opened_at,
        reason: str = "",
        payment_transaction: PaymentTransaction | None = None,
        due_at=None,
        raw_payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentDispute:
        """
        Create or update a dispute case from provider data.
        """
        if not provider_dispute_id:
            raise PaymentError("Provider dispute ID is required.")

        raw_payload = raw_payload or {}
        metadata = metadata or {}

        dispute = get_payment_dispute_by_provider_dispute_id(
            provider=provider,
            provider_dispute_id=provider_dispute_id,
        )

        if dispute is not None:
            dispute.payment_intent = payment_intent
            setattr(cast(Any, dispute), "payment_transaction", payment_transaction)
            dispute.amount = amount
            dispute.currency = currency
            dispute.reason = reason
            dispute.status = PaymentDisputeStatus.OPEN
            dispute.opened_at = opened_at
            dispute.due_at = due_at
            dispute.raw_payload = raw_payload
            dispute.metadata = metadata
            dispute.save(
                update_fields=[
                    "payment_intent",
                    "payment_transaction",
                    "amount",
                    "currency",
                    "reason",
                    "status",
                    "opened_at",
                    "due_at",
                    "raw_payload",
                    "metadata",
                    "updated_at",
                ]
            )
            return dispute

        return PaymentDispute.objects.create(
            payment_intent=payment_intent,
            payment_transaction=payment_transaction,
            provider=provider,
            provider_dispute_id=provider_dispute_id,
            status=PaymentDisputeStatus.OPEN,
            reason=reason,
            amount=amount,
            currency=currency,
            opened_at=opened_at,
            due_at=due_at,
            raw_payload=raw_payload,
            metadata=metadata,
        )

    @staticmethod
    def mark_under_review(
        *,
        dispute: PaymentDispute,
    ) -> PaymentDispute:
        """
        Mark a dispute as under review.
        """
        dispute.status = PaymentDisputeStatus.UNDER_REVIEW
        dispute.save(update_fields=["status", "updated_at"])
        return dispute

    @staticmethod
    def resolve_won(
        *,
        dispute: PaymentDispute,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentDispute:
        """
        Mark dispute as won.
        """
        metadata = metadata or {}

        merged_metadata = dispute.metadata or {}
        merged_metadata.update(metadata)

        dispute.status = PaymentDisputeStatus.WON
        dispute.resolved_at = timezone.now()
        dispute.metadata = merged_metadata
        dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "metadata",
                "updated_at",
            ]
        )
        return dispute

    @staticmethod
    def resolve_lost(
        *,
        dispute: PaymentDispute,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentDispute:
        """
        Mark dispute as lost.
        """
        metadata = metadata or {}

        merged_metadata = dispute.metadata or {}
        merged_metadata.update(metadata)

        dispute.status = PaymentDisputeStatus.LOST
        dispute.resolved_at = timezone.now()
        dispute.metadata = merged_metadata
        dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "metadata",
                "updated_at",
            ]
        )
        return dispute

    @staticmethod
    def close_dispute(
        *,
        dispute: PaymentDispute,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentDispute:
        """
        Close a dispute after final handling.
        """
        metadata = metadata or {}

        merged_metadata = dispute.metadata or {}
        merged_metadata.update(metadata)

        dispute.status = PaymentDisputeStatus.CLOSED
        if dispute.resolved_at is None:
            dispute.resolved_at = timezone.now()
        dispute.metadata = merged_metadata
        dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "metadata",
                "updated_at",
            ]
        )
        return dispute