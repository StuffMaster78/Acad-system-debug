from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.exceptions import DiscountValidationError
from discounts.models.discount import Discount
from discounts.models.discount_spend_tier import DiscountSpendTier
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.discount_validation_service import (
    DiscountValidationService,
)
from websites.models.websites import Website


class DiscountValidationServiceTests(TestCase):
    """
    Tests for client discount validation.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Site A",
            domain="site-a.test",
        )
        self.other_website = Website.objects.create(
            name="Site B",
            domain="site-b.test",
        )

        user_model = get_user_model()

        self.client_user = user_model.objects.create_user(
            username="TestUser2",
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.other_client = user_model.objects.create_user(
            username="TestingUser",
            email="other@example.com",
            password="pass",
            website=self.other_website,
        )

        self.discount = Discount.objects.create(
            website=self.website,
            discount_code="SAVE10",
            name="Save 10",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            min_payable_amount=Decimal("50.00"),
            origin=DiscountOrigin.MANUAL,
            is_active=True,
        )

    def test_valid_discount_passes(self) -> None:
        result = DiscountValidationService.validate_for_client(
            discount=self.discount,
            website=self.website,
            client=self.client,
            subtotal=Decimal("100.00"),
        )

        self.assertEqual(result, self.discount)

    def test_cross_tenant_client_is_rejected(self) -> None:
        with self.assertRaises(DiscountValidationError):
            DiscountValidationService.validate_for_client(
                discount=self.discount,
                website=self.website,
                client=self.other_client,
                subtotal=Decimal("100.00"),
            )

    def test_minimum_payable_is_enforced(self) -> None:
        with self.assertRaises(DiscountValidationError):
            DiscountValidationService.validate_for_client(
                discount=self.discount,
                website=self.website,
                client=self.client,
                subtotal=Decimal("20.00"),
            )

    def test_inactive_campaign_is_rejected(self) -> None:
        campaign = PromotionalCampaign.objects.create(
            website=self.website,
            name="Black Friday",
            slug="black-friday",
            is_active=False,
        )
        Discount.objects.filter(pk=self.discount.pk).update(
            campaign=campaign,
        )
        self.discount.refresh_from_db()

        with self.assertRaises(DiscountValidationError):
            DiscountValidationService.validate_for_client(
                discount=self.discount,
                website=self.website,
                client=self.client,
                subtotal=Decimal("100.00"),
            )

    def test_first_order_discount_rejects_existing_customer(self) -> None:
        self.discount.first_order_only = True
        self.discount.save(update_fields=["first_order_only"])

        with self.assertRaises(DiscountValidationError):
            DiscountValidationService.validate_for_client(
                discount=self.discount,
                website=self.website,
                client=self.client,
                subtotal=Decimal("100.00"),
                has_prior_paid_purchase=True,
            )

    def test_spend_tier_requires_enough_lifetime_spend(self) -> None:
        tier_discount = Discount.objects.create(
            website=self.website,
            discount_code="GOLD10",
            name="Gold",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            origin=DiscountOrigin.SPEND_TIER,
            is_active=True,
        )
        DiscountSpendTier.objects.create(
            website=self.website,
            discount=tier_discount,
            name="Gold tier",
            minimum_lifetime_spend=Decimal("1000.00"),
            is_active=True,
        )

        with self.assertRaises(DiscountValidationError):
            DiscountValidationService.validate_for_client(
                discount=tier_discount,
                website=self.website,
                client=self.client,
                subtotal=Decimal("100.00"),
                lifetime_spend=Decimal("500.00"),
            )