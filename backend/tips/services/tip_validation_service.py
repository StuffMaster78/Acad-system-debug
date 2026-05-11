from __future__ import annotations

from decimal import Decimal

from tips.exceptions import TipValidationError
from tips.models.tip_policy import TipPolicy


class TipValidationService:
    """
    Ensures tip amount integrity.
    """

    @staticmethod
    def validate(
        *,
        policy: TipPolicy,
        amount: Decimal,
    ) -> None:

        if amount <= Decimal("0"):
            raise TipValidationError("Invalid tip amount.")

        if amount < policy.minimum_tip_amount:
            raise TipValidationError("Below minimum tip.")

        if amount > Decimal("1000000"):
            raise TipValidationError("Exceeds system limit.")