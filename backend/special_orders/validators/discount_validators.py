from __future__ import annotations

from decimal import Decimal


class DiscountValidator:
    """
    Ensures discount sanity.
    """

    @staticmethod
    def validate_percentage(value: Decimal):
        if value < 0 or value > 100:
            raise ValueError("Percentage must be between 0 and 100.")

    @staticmethod
    def validate_not_exceed_total(*, discount_amount, total_amount):
        if discount_amount > total_amount:
            raise ValueError("Discount cannot exceed total amount.")