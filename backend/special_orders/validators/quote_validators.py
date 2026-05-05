from __future__ import annotations

from decimal import Decimal


class QuoteValidator:
    """
    Validates quote construction and transitions.
    """

    @staticmethod
    def validate_total_matches_lines(*, total_amount, lines_total):
        if total_amount != lines_total:
            raise ValueError("Quote total does not match sum of lines.")

    @staticmethod
    def validate_positive_amount(amount: Decimal):
        if amount <= 0:
            raise ValueError("Quote amount must be positive.")