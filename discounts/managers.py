from django.db import models
from discounts.models import Discount, PromotionalCampaign

class DiscountQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def all_with_deleted(self):
        return self.all()


class DiscountManager:
    """Manager for Discount model with custom querysets and creation methods."""
    def __init__(self):
        self.queryset = DiscountQuerySet(Discount)
    @staticmethod
    def create_with_campaign(code, value, campaign_slug, **kwargs):
        """
        Create a new discount associated with a promotional campaign.
        Args:
            code (str): Discount code.
            value (float): Discount value.
            campaign_slug (str): Slug of the promotional campaign.
            **kwargs: Additional fields for the Discount model.
        Returns:
            Discount: The created discount instance.
        """
        campaign = PromotionalCampaign.objects.get(slug=campaign_slug)
        return Discount.objects.create(
            code=code,
            value=value,
            promotional_campaign=campaign,
            **kwargs
        )