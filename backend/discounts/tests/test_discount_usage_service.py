from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.constants import PayableType
from discounts.exceptions import DiscountAlreadyAppliedError
from discounts.models.discount import Discount
from discounts.services.discount_resolution_service import ResolvedDiscount
from discounts.services.discount_usage_service import DiscountUsageService
from websites.models.websites import Website


class DiscountUsageServiceTests(TestCase):
    """
    Tests for immutable discount usage creation.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Site A",
            domain="site-a.test",
        )
        user_model = get_user_model()

        self.client_user = user_model.objects.create_user(
            username="TestUseri",
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.discount = Discount.objects.create(
            website=self.website,
            discount_code="SAVE10",
            name="Save 10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            origin=DiscountOrigin.MANUAL,
            is_active=True,
        )
        self.resolved = ResolvedDiscount(
            discount=self.discount,
            discount_code="SAVE10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            discount_amount=Decimal("10.00"),
            final_amount=Decimal("90.00"),
            origin=DiscountOrigin.MANUAL,
            source="entered_code",
        )

    def test_create_usage(self) -> None:
        usage = DiscountUsageService.create_usage(
            website=self.website,
            client=self.client,
            resolved_discount=self.resolved,
            subtotal=Decimal("100.00"),
            payable_type=PayableType.ORDER,
            payable_id="order-1",
        )

        self.assertEqual(usage.discount_code, "SAVE10")
        self.assertEqual(usage.discount_amount, Decimal("10.00"))

    def test_one_discount_per_payable_is_enforced(self) -> None:
        kwargs = {
            "website": self.website,
            "client": self.client,
            "resolved_discount": self.resolved,
            "subtotal": Decimal("100.00"),
            "payable_type": PayableType.ORDER,
            "payable_id": "order-1",
        }

        DiscountUsageService.create_usage(**kwargs)

        with self.assertRaises(DiscountAlreadyAppliedError):
            DiscountUsageService.create_usage(**kwargs)