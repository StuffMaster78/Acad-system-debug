from __future__ import annotations

from django.db import transaction

from discounts.exceptions import DiscountConfigurationError
from discounts.models.discount import Discount
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.discount_notification_service import (
    DiscountNotificationEvent,
    DiscountNotificationService,
)

class CampaignLifecycleService:
    """
    Campaign activation and deactivation logic.
    """

    @staticmethod
    @transaction.atomic
    def activate_campaign(
        *,
        campaign: PromotionalCampaign,
        updated_by=None,
    ) -> PromotionalCampaign:
        """
        Activate campaign and its linked discounts.
        """
        CampaignLifecycleService._validate_campaign(campaign=campaign)

        campaign.is_active = True
        campaign.is_archived = False
        campaign.updated_by = updated_by
        campaign.save(
            update_fields=[
                "is_active",
                "is_archived",
                "updated_by",
                "updated_at",
            ]
        )



        Discount.objects.filter(
            website=campaign.website,
            campaign=campaign,
            is_deleted=False,
            is_campaign_managed=True,
        ).update(
            is_active=True,
            is_archived=False,
            updated_by=updated_by,
        )

        if updated_by is not None:
            DiscountNotificationService.notify_campaign_event(
                campaign=campaign,
                event_key=DiscountNotificationEvent.CAMPAIGN_ACTIVATED,
                recipient=updated_by,
                triggered_by=updated_by,
            )

        return campaign

    @staticmethod
    @transaction.atomic
    def deactivate_campaign(
        *,
        campaign: PromotionalCampaign,
        updated_by=None,
    ) -> PromotionalCampaign:
        """
        Deactivate campaign and its linked discounts.
        """
        CampaignLifecycleService._validate_campaign(campaign=campaign)

        campaign.is_active = False
        campaign.updated_by = updated_by
        campaign.save(
            update_fields=[
                "is_active",
                "updated_by",
                "updated_at",
            ]
        )

        Discount.objects.filter(
            website=campaign.website,
            campaign=campaign,
            is_deleted=False,
            is_campaign_managed=True,
        ).update(
            is_active=False,
            updated_by=updated_by,
        )

        return campaign

    @staticmethod
    def _validate_campaign(*, campaign: PromotionalCampaign) -> None:
        """
        Ensure campaign has a valid tenant website.
        """
        if not campaign or not getattr(campaign, "id", None):
            raise DiscountConfigurationError(
                "A persisted campaign is required."
            )

        if not getattr(campaign, "website_id", None):
            raise DiscountConfigurationError(
                "Campaign must belong to a website."
            )