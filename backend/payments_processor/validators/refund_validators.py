from __future__ import annotations

from decimal import Decimal

from payments_processor.enums import PaymentIntentStatus, RefundDestination
from payments_processor.exceptions import PaymentError


def validate_refund_amount(amount: Decimal) -> None:
    """
    Ensure refund amount is valid.

    Args:
        amount: Refund amount.

    Raises:
        PaymentError: If amount is invalid.
    """
    if amount <= Decimal("0.00"):
        raise PaymentError("Refund amount must be greater than zero.")


def validate_refund_destination(destination: str) -> None:
    """
    Ensure refund destination is supported.

    Args:
        destination: Refund destination.

    Raises:
        PaymentError: If destination is invalid.
    """
    if destination not in RefundDestination.values:
        raise PaymentError(
            f"Unsupported refund destination '{destination}'."
        )


def validate_refundable_payment(payment_intent) -> None:
    """
    Ensure payment is eligible for refund.

    Args:
        payment_intent: PaymentIntent instance.

    Raises:
        PaymentError: If payment is not refundable.
    """
    if payment_intent.status not in {
        PaymentIntentStatus.SUCCEEDED,
        PaymentIntentStatus.PARTIALLY_REFUNDED,
    }:
        raise PaymentError(
            f"Payment '{payment_intent.reference}' is not refundable."
        )


def validate_refund_balance(
    *,
    payment_intent,
    amount: Decimal,
) -> None:
    """
    Ensure refund does not exceed available refundable balance.

    Args:
        payment_intent: PaymentIntent instance.
        amount: Refund amount.

    Raises:
        PaymentError: If refund exceeds available amount.
    """
    refundable = payment_intent.amount - payment_intent.amount_refunded

    if amount > refundable:
        raise PaymentError(
            "Refund amount exceeds refundable balance."
        )