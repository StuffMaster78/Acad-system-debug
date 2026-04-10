from __future__ import annotations

from datetime import datetime
from typing import Any

from django.utils import timezone

from payments_processor.models.payment_intent import PaymentIntent
from payments_processor.models.payment_transaction import PaymentTransaction


class PaymentTransactionService:
    """
    Handles creation of provider transaction records.
    """

    @staticmethod
    def create_transaction(
        *,
        payment_intent: PaymentIntent,
        provider: str,
        kind: str,
        status: str,
        amount,
        currency: str,
        provider_transaction_id: str = "",
        provider_event_id: str = "",
        raw_payload: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> PaymentTransaction:
        """
        Create and return a payment transaction record.
        """
        return PaymentTransaction.objects.create(
            payment_intent=payment_intent,
            provider=provider,
            kind=kind,
            status=status,
            amount=amount,
            currency=currency,
            provider_transaction_id=provider_transaction_id or "",
            provider_event_id=provider_event_id or "",
            raw_payload=raw_payload or {},
            occurred_at=occurred_at,
            processed_at=timezone.now(),
        )