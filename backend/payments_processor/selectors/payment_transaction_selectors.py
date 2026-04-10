from __future__ import annotations

from typing import Optional

from payments_processor.models import PaymentTransaction


def get_transaction_by_provider_event_id(
    *,
    provider: str,
    provider_event_id: str,
) -> Optional[PaymentTransaction]:
    """
    Return a payment transaction by provider event ID.
    """
    return (
        PaymentTransaction.objects.select_related("payment_intent")
        .filter(
            provider=provider,
            provider_event_id=provider_event_id,
        )
        .first()
    )


def get_transaction_by_provider_transaction_id(
    *,
    provider: str,
    provider_transaction_id: str,
) -> Optional[PaymentTransaction]:
    """
    Return a payment transaction by provider transaction ID.
    """
    return (
        PaymentTransaction.objects.select_related("payment_intent")
        .filter(
            provider=provider,
            provider_transaction_id=provider_transaction_id,
        )
        .first()
    )


def get_transactions_for_payment_intent(
    *,
    payment_intent_id: int,
):
    """
    Return all transactions for a payment intent, newest first.
    """
    return (
        PaymentTransaction.objects.filter(
            payment_intent_id=payment_intent_id,
        )
        .order_by("-created_at")
    )


def get_latest_transaction_for_payment_intent(
    *,
    payment_intent_id: int,
) -> Optional[PaymentTransaction]:
    """
    Return the latest transaction for a payment intent.
    """
    return (
        PaymentTransaction.objects.filter(
            payment_intent_id=payment_intent_id,
        )
        .order_by("-created_at")
        .first()
    )


def payment_transaction_exists_for_event(
    *,
    provider: str,
    provider_event_id: str,
) -> bool:
    """
    Return True if a transaction already exists for a provider event.
    """
    return PaymentTransaction.objects.filter(
        provider=provider,
        provider_event_id=provider_event_id,
    ).exists()