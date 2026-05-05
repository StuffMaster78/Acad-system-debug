from __future__ import annotations

from django.db import transaction
from django.utils.text import slugify

from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.models.discount import Discount
from discounts.validators.campaign_validators import CampaignValidator
from discounts.services.discount_notification_service import (
    DiscountNotificationEvent,
    DiscountNotificationService,
)

class CampaignAdminService:
    """
    Admin write operations for promotional campaigns.
    """

    @staticmethod
    @transaction.atomic
    def create_campaign(
        *,
        website,
        name: str,
        created_by=None,
        slug: str | None = None,
        description: str = "",
        starts_at=None,
        ends_at=None,
        is_active: bool = False,
    ) -> PromotionalCampaign:
        """
        Create a promotional campaign.
        """
        CampaignValidator.validate_date_window(
            starts_at=starts_at,
            ends_at=ends_at,
        )

        campaign_slug = slug or slugify(name)


        return PromotionalCampaign.objects.create(
            website=website,
            name=name,
            slug=campaign_slug,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active,
            is_archived=False,
            created_by=created_by,
            updated_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def update_campaign(
        *,
        campaign: PromotionalCampaign,
        updated_by=None,
        **fields,
    ) -> PromotionalCampaign:
        """
        Update a promotional campaign.
        """
        starts_at = fields.get("starts_at", campaign.starts_at)
        ends_at = fields.get("ends_at", campaign.ends_at)

        CampaignValidator.validate_date_window(
            starts_at=starts_at,
            ends_at=ends_at,
        )

        for field, value in fields.items():
            setattr(campaign, field, value)

        campaign.updated_by = updated_by
        campaign.save()

        return campaign

    @staticmethod
    @transaction.atomic
    def archive_campaign(
        *,
        campaign: PromotionalCampaign,
        updated_by=None,
    ) -> PromotionalCampaign:
        """
        Archive a campaign and disable all linked discounts.
        """
        campaign.is_archived = True
        campaign.is_active = False
        campaign.updated_by = updated_by
        campaign.save(
            update_fields=[
                "is_archived",
                "is_active",
                "updated_by",
                "updated_at",
            ]
        )

        Discount.objects.filter(campaign=campaign).update(
            is_active=False,
            updated_by=updated_by,
        )
        
        if updated_by is not None:
            DiscountNotificationService.notify_campaign_event(
                campaign=campaign,
                event_key=DiscountNotificationEvent.CAMPAIGN_ARCHIVED,
                recipient=updated_by,
                triggered_by=updated_by,
            )

        return campaign
    
    @staticmethod
    @transaction.atomic
    def restore_campaign(
        *,
        campaign: PromotionalCampaign,
        updated_by=None,
    ) -> PromotionalCampaign:
        """
        Restore an archived campaign without activating it.
        """
        campaign.is_archived = False
        campaign.updated_by = updated_by
        campaign.save(
            update_fields=[
                "is_archived",
                "updated_by",
                "updated_at",
            ]
        )
        if updated_by is not None:
            DiscountNotificationService.notify_campaign_event(
                campaign=campaign,
                event_key=DiscountNotificationEvent.CAMPAIGN_RESTORED,
                recipient=updated_by,
                triggered_by=updated_by,
            )

        return campaign