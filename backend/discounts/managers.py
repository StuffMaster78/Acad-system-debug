from django.db import models
class DiscountQuerySet(models.QuerySet):
    """
    Custom queryset for Discount model with methods for
    filtering active and deleted discounts."""
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def all_with_deleted(self):
        return self.all()


class DiscountManager:
    """Manager for Discount model with custom querysets and creation methods."""
    def __init__(self):
        """
        Initialize the DiscountManager with a custom queryset.
        This manager is used to handle Discount objects and their associated
        promotional campaigns.
        """
        # Import the Discount model here to avoid circular imports
        from discounts.models import Discount
        # Initialize the queryset with the Discount model
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
        from discounts.models import Discount
        from discounts.models import PromotionalCampaign
        # Fetch the promotional campaign by its slug
        if not campaign_slug:
            raise ValueError("Campaign slug must be provided.")
        if not code:
            raise ValueError("Discount code must be provided.")
        if not value:
            raise ValueError("Discount value must be provided.")
        if not isinstance(value, (int, float)):
            raise ValueError("Discount value must be a number.")
        campaign = PromotionalCampaign.objects.get(slug=campaign_slug)
        return Discount.objects.create(
            code=code,
            value=value,
            promotional_campaign=campaign,
            **kwargs
        )