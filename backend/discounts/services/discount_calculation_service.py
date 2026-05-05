from __future__ import annotations

from decimal import Decimal
from decimal import ROUND_HALF_UP

from discounts.constants import DiscountType
from discounts.exceptions import DiscountConfigurationError


class DiscountCalculationService:
    """
    Calculate discount amounts.

    This service does not validate eligibility. It only calculates the
    monetary value of a valid discount against a subtotal.
    """

    MONEY_QUANT = Decimal("0.01")

    @classmethod
    def calculate_amount(cls, *, discount, subtotal: Decimal) -> Decimal:
        """
        Return the discount amount for a subtotal.
        """
        subtotal = cls._money(subtotal)

        if subtotal <= Decimal("0.00"):
            return Decimal("0.00")

        if discount.discount_type == DiscountType.PERCENTAGE:
            amount = cls._calculate_percentage(
                value=discount.discount_value,
                subtotal=subtotal,
            )
        elif discount.discount_type == DiscountType.FIXED_AMOUNT:
            amount = cls._calculate_fixed(
                value=discount.discount_value,
                subtotal=subtotal,
            )
        else:
            raise DiscountConfigurationError(
                "Unsupported discount type."
            )

        amount = cls._apply_maximum(discount=discount, amount=amount)

        return min(cls._money(amount), subtotal)

    @classmethod
    def calculate_final_amount(
        cls,
        *,
        discount,
        subtotal: Decimal,
    ) -> Decimal:
        """
        Return final amount after applying a discount.
        """
        subtotal = cls._money(subtotal)
        amount = cls.calculate_amount(
            discount=discount,
            subtotal=subtotal,
        )

        return cls._money(subtotal - amount)

    @classmethod
    def _calculate_percentage(
        cls,
        *,
        value: Decimal,
        subtotal: Decimal,
    ) -> Decimal:
        """
        Return percentage based discount amount.
        """
        if value <= Decimal("0.00") or value > Decimal("100.00"):
            raise DiscountConfigurationError(
                "Percentage discount must be greater than 0 "
                "and less than or equal to 100."
            )

        return subtotal * value / Decimal("100.00")

    @classmethod
    def _calculate_fixed(
        cls,
        *,
        value: Decimal,
        subtotal: Decimal,
    ) -> Decimal:
        """
        Return fixed discount amount.
        """
        if value <= Decimal("0.00"):
            raise DiscountConfigurationError(
                "Fixed discount value must be greater than zero."
            )

        return min(value, subtotal)

    @classmethod
    def _apply_maximum(cls, *, discount, amount: Decimal) -> Decimal:
        """
        Cap the discount amount if a maximum is configured.
        """
        maximum = discount.max_discount_amount

        if maximum is None:
            return amount

        maximum = cls._money(maximum)

        if maximum <= Decimal("0.00"):
            raise DiscountConfigurationError(
                "Maximum discount amount must be greater than zero."
            )

        return min(amount, maximum)

    @classmethod
    def _money(cls, value: Decimal) -> Decimal:
        """
        Normalize a decimal value to two currency places.
        """
        return value.quantize(cls.MONEY_QUANT, rounding=ROUND_HALF_UP)