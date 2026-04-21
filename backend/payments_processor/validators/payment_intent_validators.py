from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.enums import PaymentIntentPurpose, PaymentProvider
from payments_processor.exceptions import PaymentError


def validate_payment_intent_amount(amount: Decimal) -> None:
    """
    Ensure payment intent amount is positive.

    Args:
        amount: Intended payment amount.

    Raises:
        PaymentError: If amount is not greater than zero.
    """
    if amount <= Decimal("0.00"):
        raise PaymentError("Payment amount must be greater than zero.")


def validate_payment_provider(provider: str) -> None:
    """
    Ensure provider is supported.

    Args:
        provider: Payment provider string.

    Raises:
        PaymentError: If provider is not supported.
    """
    if provider not in PaymentProvider.values:
        raise PaymentError(f"Unsupported payment provider '{provider}'.")


def validate_payment_purpose(purpose: str) -> None:
    """
    Ensure payment purpose is supported.

    Args:
        purpose: Payment purpose string.

    Raises:
        PaymentError: If purpose is invalid.
    """
    if purpose not in PaymentIntentPurpose.values:
        raise PaymentError(f"Unsupported payment purpose '{purpose}'.")


def validate_payable_presence(
    *,
    purpose: str,
    payable: Any | None,
) -> None:
    """
    Ensure payable exists where required.

    Wallet top-up may not require a payable.

    Args:
        purpose: Payment purpose.
        payable: Related domain object.

    Raises:
        PaymentError: If payable is required but missing.
    """
    if purpose == PaymentIntentPurpose.WALLET_TOP_UP:
        return

    if payable is None:
        raise PaymentError(
            f"Payable object is required for purpose '{purpose}'."
        )