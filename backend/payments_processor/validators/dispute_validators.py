from __future__ import annotations

from decimal import Decimal

from payments_processor.exceptions import PaymentError


def validate_dispute_amount(amount: Decimal) -> None:
    """
    Ensure dispute amount is valid.

    Args:
        amount: Dispute amount.

    Raises:
        PaymentError: If amount is invalid.
    """
    if amount <= Decimal("0.00"):
        raise PaymentError("Dispute amount must be greater than zero.")


def validate_provider_dispute_id(dispute_id: str) -> None:
    """
    Ensure provider dispute ID is present.

    Args:
        dispute_id: Provider dispute ID.

    Raises:
        PaymentError: If missing.
    """
    if not dispute_id:
        raise PaymentError("Provider dispute ID is required.")


def validate_dispute_payment_link(payment_intent) -> None:
    """
    Ensure dispute is linked to a payment.

    Args:
        payment_intent: PaymentIntent instance.

    Raises:
        PaymentError: If missing.
    """
    if payment_intent is None:
        raise PaymentError("Dispute must reference a payment intent.")