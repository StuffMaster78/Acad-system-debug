from __future__ import annotations

from typing import Optional

from payments_processor.enums import PaymentDisputeStatus
from payments_processor.models import PaymentDispute


def get_payment_dispute_by_id(dispute_id: int) -> Optional[PaymentDispute]:
    """
    Return a payment dispute by primary key.
    """
    return (
        PaymentDispute.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(id=dispute_id)
        .first()
    )


def get_payment_dispute_by_provider_dispute_id(
    *,
    provider: str,
    provider_dispute_id: str,
) -> Optional[PaymentDispute]:
    """
    Return a payment dispute by provider dispute ID.
    """
    return (
        PaymentDispute.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(
            provider=provider,
            provider_dispute_id=provider_dispute_id,
        )
        .first()
    )


def get_open_disputes():
    """
    Return disputes that still require attention.
    """
    return (
        PaymentDispute.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(
            status__in=[
                PaymentDisputeStatus.OPEN,
                PaymentDisputeStatus.UNDER_REVIEW,
            ]
        )
        .order_by("opened_at")
    )


def get_disputes_for_payment_intent(payment_intent_id: int):
    """
    Return disputes for a payment intent, newest first.
    """
    return (
        PaymentDispute.objects.select_related(
            "payment_transaction",
        )
        .filter(payment_intent_id=payment_intent_id)
        .order_by("-opened_at")
    )