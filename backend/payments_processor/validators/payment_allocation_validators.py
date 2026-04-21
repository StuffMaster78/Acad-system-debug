from __future__ import annotations

from decimal import Decimal
from typing import Any

from payments_processor.enums import PaymentAllocationType
from payments_processor.exceptions import PaymentError


def validate_allocation_amount(amount: Decimal) -> None:
    """
    Ensure allocation amount is valid.

    Args:
        amount: Allocation amount.

    Raises:
        PaymentError: If amount is not positive.
    """
    if amount <= Decimal("0.00"):
        raise PaymentError("Allocation amount must be greater than zero.")


def validate_wallet_allocation(
    *,
    allocation_type: str,
    wallet_hold: Any | None,
    payment_intent: Any | None,
) -> None:
    """
    Validate wallet-backed allocation.

    Args:
        allocation_type: Allocation type.
        wallet_hold: Wallet hold instance.
        payment_intent: Payment intent instance.

    Raises:
        PaymentError: If validation fails.
    """
    if allocation_type != PaymentAllocationType.WALLET:
        return

    if wallet_hold is None:
        raise PaymentError(
            "Wallet allocation requires a wallet hold."
        )

    if payment_intent is not None:
        raise PaymentError(
            "Wallet allocation cannot reference payment intent."
        )


def validate_external_allocation(
    *,
    allocation_type: str,
    wallet_hold: Any | None,
    payment_intent: Any | None,
) -> None:
    """
    Validate external payment allocation.

    Args:
        allocation_type: Allocation type.
        wallet_hold: Wallet hold instance.
        payment_intent: Payment intent instance.

    Raises:
        PaymentError: If validation fails.
    """
    if allocation_type != PaymentAllocationType.EXTERNAL_PAYMENT:
        return

    if payment_intent is None:
        raise PaymentError(
            "External allocation requires a payment intent."
        )

    if wallet_hold is not None:
        raise PaymentError(
            "External allocation cannot reference wallet hold."
        )


def validate_allocation_context(
    *,
    website: Any,
    customer: Any,
    wallet_hold: Any | None,
    payment_intent: Any | None,
) -> None:
    """
    Ensure allocation references belong to same tenant context.

    Args:
        website: Website instance.
        customer: User instance.
        wallet_hold: Wallet hold instance.
        payment_intent: Payment intent instance.

    Raises:
        PaymentError: If context mismatch occurs.
    """
    if wallet_hold is not None:
        if wallet_hold.website_id != website.id:
            raise PaymentError(
                "Wallet hold does not belong to this website."
            )
        if wallet_hold.wallet.owner_user_id != customer.id:
            raise PaymentError(
                "Wallet hold does not belong to this customer."
            )

    if payment_intent is not None:
        if payment_intent.website_id != website.id:
            raise PaymentError(
                "Payment intent does not belong to this website."
            )
        if payment_intent.customer_id != customer.id:
            raise PaymentError(
                "Payment intent does not belong to this customer."
            )