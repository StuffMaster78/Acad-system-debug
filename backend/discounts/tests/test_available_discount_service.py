from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.models.discount import Discount
from discounts.models.discount_spend_tier import DiscountSpendTier
from discounts.services.available_discount_service import (
    AvailableDiscountService,
)
from websites.models.websites import Website


class AvailableDiscountServiceTests(TestCase):
    """
    Tests for client-facing available discount options.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Site A",
            domain="site-a.test",
        )
        user_model = get_user_model()

        self.client_user = user_model.objects.create_user(
            username="TestUserio",
            email="client@example.com",
            password="pass",
            website=self.website,
        )

    def test_lists_standard_discount(self) -> None:
        Discount.objects.create(
            website=self.website,
            discount_code="SAVE10",
            name="Save 10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            origin=DiscountOrigin.MANUAL,
            is_active=True,
        )

        discounts = AvailableDiscountService.list_available_for_client(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
        )

        self.assertEqual(len(discounts), 1)
        self.assertEqual(discounts[0].discount_code, "SAVE10")

    def test_lists_qualified_tier_discount(self) -> None:
        discount = Discount.objects.create(
            website=self.website,
            discount_code="GOLD10",
            name="Gold 10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            origin=DiscountOrigin.SPEND_TIER,
            is_active=True,
        )
        DiscountSpendTier.objects.create(
            website=self.website,
            discount=discount,
            name="Gold",
            minimum_lifetime_spend=Decimal("1000.00"),
            is_active=True,
        )

        discounts = AvailableDiscountService.list_available_for_client(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
            lifetime_spend=Decimal("1200.00"),
        )

        codes = [item.discount_code for item in discounts]

        self.assertIn("GOLD10", codes)

    def test_hides_unqualified_tier_discount(self) -> None:
        discount = Discount.objects.create(
            website=self.website,
            discount_code="GOLD10",
            name="Gold 10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            origin=DiscountOrigin.SPEND_TIER,
            is_active=True,
        )
        DiscountSpendTier.objects.create(
            website=self.website,
            discount=discount,
            name="Gold",
            minimum_lifetime_spend=Decimal("1000.00"),
            is_active=True,
        )

        discounts = AvailableDiscountService.list_available_for_client(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
            lifetime_spend=Decimal("500.00"),
        )

        self.assertEqual(discounts, [])