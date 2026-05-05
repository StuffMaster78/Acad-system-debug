from __future__ import annotations

from django.utils import timezone

from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.services.campaign_lifecycle_service import (
    CampaignLifecycleService,
)


class CampaignSchedulerService:
    """
    Scheduled campaign activation/deactivation service.

    Intended to be called by Celery beat or a management command.
    """

    @staticmethod
    def run(*, triggered_by=None) -> dict[str, int]:
        """
        Activate due campaigns and deactivate expired campaigns.
        """
        now = timezone.now()

        due_campaigns = PromotionalCampaign.objects.filter(
            is_active=False,
            is_archived=False,
            starts_at__isnull=False,
            starts_at__lte=now,
        ).filter(
            ends_at__isnull=True,
        ) | PromotionalCampaign.objects.filter(
            is_active=False,
            is_archived=False,
            starts_at__isnull=False,
            starts_at__lte=now,
            ends_at__gt=now,
        )

        expired_campaigns = PromotionalCampaign.objects.filter(
            is_active=True,
            is_archived=False,
            ends_at__isnull=False,
            ends_at__lte=now,
        )

        activated = 0
        deactivated = 0

        for campaign in due_campaigns.distinct():
            CampaignLifecycleService.activate_campaign(
                campaign=campaign,
                updated_by=triggered_by,
            )
            activated += 1

        for campaign in expired_campaigns.distinct():
            CampaignLifecycleService.deactivate_campaign(
                campaign=campaign,
                updated_by=triggered_by,
            )
            deactivated += 1

        return {
            "activated": activated,
            "deactivated": deactivated,
        }