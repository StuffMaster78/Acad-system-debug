from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.constants import PayableType
from discounts.models.discount import Discount
from discounts.services.discount_application_service import (
    DiscountApplicationService,
)
from websites.models.websites import Website


class DiscountApplicationServiceTests(TestCase):
    """
    Tests for previewing and applying discounts.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Site A",
            domain="site-a.test",
        )
        user_model = get_user_model()

        self.client_user = user_model.objects.create_user(
            username="testUser",
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

    def test_preview_resolves_entered_code(self) -> None:
        resolved = DiscountApplicationService.preview(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
            payable_type=PayableType.ORDER,
            has_prior_paid_purchase=True,
            entered_code="SAVE10",
        )

        self.assertIsNotNone(resolved)

        if resolved is None:
            self.fail("Expected discount to resolve.")

        self.assertEqual(resolved.discount_code, "SAVE10")

    def test_apply_is_idempotent_for_same_payable(self) -> None:
        usage = DiscountApplicationService.apply(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
            payable_type=PayableType.ORDER,
            payable_id="order-1",
            has_prior_paid_purchase=True,
            entered_code="SAVE10",
        )
        second = DiscountApplicationService.apply(
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
            payable_type=PayableType.ORDER,
            payable_id="order-1",
            has_prior_paid_purchase=True,
            entered_code="SAVE10",
        )

        self.assertIsNotNone(usage)
        self.assertIsNotNone(second)

        if usage is None or second is None:
            self.fail("Expected usage records.")

        self.assertEqual(usage.pk, second.pk)