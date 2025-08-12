"""
Service for handling promotionl campaigns and their associated discounts.
"""

import logging
from decimal import Decimal, ROUND_HALF_UP

from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from discounts.utils import get_discount_model
from notifications_system.services.dispatch import NotificationDispatcher

logger = logging.getLogger(__name__)


def get_order_model():
    return apps.get_model('orders', 'Order')


class PromotionalCampaignService:
    """
    Service for handling promotional campaigns and their associated discounts.
    """

    @staticmethod
    def get_promotional_campaign_model():
        """
        Returns the PromotionalCampaign model from the discounts app.
        This allows for dynamic loading of the model to avoid circular imports.
        """
        return apps.get_model('discounts', 'PromotionalCampaign')

    @classmethod
    def get_active_seasonal_events(cls, website):
        """
        Retrieve all active promotional campaigns for a given website.

        Args:
            website (Website): The website for which to retrieve events.

        Returns:
            QuerySet: Active SeasonalEvent objects for the website.
        """
        current_time = now()
        PromotionalCampaign = cls.get_promotional_campaign_model()
        return PromotionalCampaign.objects.filter(
            website=website,
            is_active=True,
            start_date__lte=current_time,
            end_date__gte=current_time,
        )

    @classmethod
    def mark_expired_events(cls):
        """
        Mark all promotional campaigns that have expired as inactive.

        Returns:
            int: Number of events marked inactive.
        """
        current_time = now()
        PromotionalCampaign = cls.get_promotional_campaign_model()
        updated_count = PromotionalCampaign.objects.filter(
            end_date__lt=current_time,
            is_active=True,
        ).update(is_active=False)

        logger.info(f"Marked {updated_count} promotional campaigns as inactive.")
        return updated_count

    @staticmethod
    def attach_promotional_campaign_to_discount(discount, promotional_campaign):
        """
        Attach a promotional campaign to a discount, ensuring it aligns with
        the event's active period.

        Args:
            discount (Discount): Discount instance to attach the event to.
            seasonal_event (SeasonalEvent): SeasonalEvent instance to attach.

        Raises:
            ValidationError: If the event is inactive or outside its valid period.
        """
        current_time = now()
        if promotional_campaign.is_active and \
           promotional_campaign.start_date <= current_time <= promotional_campaign.end_date:
            discount.promotional_campaign = promotional_campaign
            try:
                discount.save()
                logger.info(
                    f"Attached promotional campaign '{promotional_campaign}' to discount '{discount.code}'."
                )
            except Exception as e:
                logger.error(f"Failed to save discount with promotional campaign: {e}")
                NotificationDispatcher.notify_errors(
                    subject="Discount Promotional Campaign Save Failure",
                    message=str(e),
                    user=discount.user,
                    context={"discount_id": discount.id, "campaign_id": promotional_campaign.id}
                )
                raise
        else:
            raise ValidationError(
                "The promotional campaign is not active or is outside its valid period."
            )

    @staticmethod
    def get_discounts_for_event(promotional_campaign):
        """
        Retrieve discounts that are part of the given promotional campaign.

        Args:
            promotional_campaign (PromotionalCampaign): The promotional campaign instance.

        Returns:
            QuerySet: Discounts linked to the promotional campaign.
        """
        Discount = get_discount_model()
        return Discount.objects.filter(promotional_campaign=promotional_campaign)

    @staticmethod
    def is_discount_applicable(discount):
        """
        Check if the discount is linked to an active promotional campaign or has no event.

        Args:
            discount (Discount): Discount instance to check.

        Returns:
            bool: True if applicable, False otherwise.
        """
        current_time = now()
        campaign = discount.promotional_campaign
        if not campaign:
            return True

        return (discount.is_active and
                campaign.is_active and
                campaign.start_date <= current_time <= campaign.end_date)