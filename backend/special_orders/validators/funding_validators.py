from __future__ import annotations

from decimal import Decimal


class FundingValidator:
    """
    Protects financial integrity.
    """

    @staticmethod
    def validate_payment_amount(*, amount: Decimal):
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

    @staticmethod
    def validate_not_overfunding(*, current_funded, total_amount, incoming):
        if current_funded + incoming > total_amount:
            raise ValueError("Payment exceeds total required amount.")

    @staticmethod
    def validate_refund_amount(*, refundable_amount, requested_amount):
        if requested_amount > refundable_amount:
            raise ValueError("Refund exceeds refundable amount.")