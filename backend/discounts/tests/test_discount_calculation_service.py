from __future__ import annotations

from decimal import Decimal

from django.test import SimpleTestCase

from discounts.constants import DiscountType
from discounts.exceptions import DiscountConfigurationError
from discounts.services.discount_calculation_service import (
    DiscountCalculationService,
)


class DummyDiscount:
    """
    Minimal discount object for calculation tests.
    """

    def __init__(
        self,
        *,
        discount_type: str,
        discount_value: Decimal,
        max_discount_amount: Decimal | None = None,
    ) -> None:
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.max_discount_amount = max_discount_amount


class DiscountCalculationServiceTests(SimpleTestCase):
    """
    Tests for discount amount calculations.
    """

    def test_percentage_discount_is_calculated(self) -> None:
        discount = DummyDiscount(
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20.00"),
        )

        amount = DiscountCalculationService.calculate_amount(
            discount=discount,
            subtotal=Decimal("100.00"),
        )

        self.assertEqual(amount, Decimal("20.00"))

    def test_fixed_discount_cannot_exceed_subtotal(self) -> None:
        discount = DummyDiscount(
            discount_type=DiscountType.FIXED_AMOUNT,
            discount_value=Decimal("150.00"),
        )

        amount = DiscountCalculationService.calculate_amount(
            discount=discount,
            subtotal=Decimal("100.00"),
        )

        self.assertEqual(amount, Decimal("100.00"))

    def test_percentage_discount_respects_maximum(self) -> None:
        discount = DummyDiscount(
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("50.00"),
            max_discount_amount=Decimal("30.00"),
        )

        amount = DiscountCalculationService.calculate_amount(
            discount=discount,
            subtotal=Decimal("100.00"),
        )

        self.assertEqual(amount, Decimal("30.00"))

    def test_zero_percentage_raises_error(self) -> None:
        discount = DummyDiscount(
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("0.00"),
        )

        with self.assertRaises(DiscountConfigurationError):
            DiscountCalculationService.calculate_amount(
                discount=discount,
                subtotal=Decimal("100.00"),
            )