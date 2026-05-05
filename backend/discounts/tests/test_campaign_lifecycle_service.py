from __future__ import annotations

from decimal import Decimal

from django.test import TestCase

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.models.discount import Discount
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.campaign_lifecycle_service import (
    CampaignLifecycleService,
)
from websites.models.websites import Website


class CampaignLifecycleServiceTests(TestCase):
    """
    Tests for campaign activation and deactivation.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Site A",
            domain="site-a.test",
        )
        self.campaign = PromotionalCampaign.objects.create(
            website=self.website,
            name="Black Friday",
            slug="black-friday",
            is_active=False,
            is_archived=False,
        )
        self.discount = Discount.objects.create(
            website=self.website,
            campaign=self.campaign,
            discount_code="BF20",
            name="Black Friday 20",
            discount_type=DiscountType.PERCENTAGE,
            discount_value=Decimal("20.00"),
            origin=DiscountOrigin.CAMPAIGN,
            is_active=False,
            is_campaign_managed=True,
        )

    def test_activate_campaign_activates_managed_discount(self) -> None:
        CampaignLifecycleService.activate_campaign(
            campaign=self.campaign,
        )

        self.campaign.refresh_from_db()
        self.discount.refresh_from_db()

        self.assertTrue(self.campaign.is_active)
        self.assertTrue(self.discount.is_active)

    def test_deactivate_campaign_deactivates_managed_discount(self) -> None:
        CampaignLifecycleService.activate_campaign(
            campaign=self.campaign,
        )
        CampaignLifecycleService.deactivate_campaign(
            campaign=self.campaign,
        )

        self.campaign.refresh_from_db()
        self.discount.refresh_from_db()

        self.assertFalse(self.campaign.is_active)
        self.assertFalse(self.discount.is_active)

    def test_unmanaged_discount_keeps_manual_state(self) -> None:
        self.discount.is_campaign_managed = False
        self.discount.is_active = False
        self.discount.save(
            update_fields=["is_campaign_managed", "is_active"],
        )

        CampaignLifecycleService.activate_campaign(
            campaign=self.campaign,
        )

        self.discount.refresh_from_db()

        self.assertFalse(self.discount.is_active)