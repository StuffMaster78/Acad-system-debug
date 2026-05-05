from __future__ import annotations

from decimal import Decimal

from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.models.discount import Discount
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.discount_clone_service import DiscountCloneService
from websites.models.websites import Website


class DiscountCloneServiceTests(TestCase):
    """
    Tests for discount and campaign cloning.
    """

    def setUp(self) -> None:
        self.source_website = Website.objects.create(
            name="Source",
            domain="source.test",
        )
        self.target_website = Website.objects.create(
            name="Target",
            domain="target.test",
        )
        self.campaign = PromotionalCampaign.objects.create(
            website=self.source_website,
            name="Holiday",
            slug="holiday",
        )
        self.discount = Discount.objects.create(
            website=self.source_website,
            campaign=self.campaign,
            discount_code="HOLIDAY20",
            name="Holiday 20",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20.00"),
            origin=DiscountOrigin.HOLIDAY,
            is_active=True,
            is_campaign_managed=True,
        )

    def test_clone_discount_to_target_website(self) -> None:
        cloned = DiscountCloneService.clone_discount(
            source_discount=self.discount,
            target_website=self.target_website,
            new_code="TARGET20",
        )

        self.assertEqual(cloned.website, self.target_website)
        self.assertEqual(cloned.discount_code, "TARGET20")

    def test_clone_campaign_clones_discounts(self) -> None:
        cloned_campaign = DiscountCloneService.clone_campaign(
            source_campaign=self.campaign,
            target_website=self.target_website,
            new_slug="holiday-target",
        )

        self.assertEqual(cloned_campaign.website, self.target_website)

        cloned_count = Discount.objects.filter(
            website=self.target_website,
            campaign=cloned_campaign,
        ).count()

        self.assertEqual(cloned_count, 1)