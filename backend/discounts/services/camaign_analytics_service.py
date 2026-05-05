from __future__ import annotations

from django.db.models import Count, Sum

from discounts.models import DiscountUsage


class CampaignAnalyticsService:
    """
    Campaign performance analytics.
    """

    @staticmethod
    def get_campaign_summary(*, campaign) -> dict:
        """
        Return performance metrics for one campaign.
        """
        usages = DiscountUsage.objects.filter(
            website=campaign.website,
            discount__campaign=campaign,
        )

        totals = usages.aggregate(
            redemptions=Count("id"),
            discount_given=Sum("discount_amount"),
            subtotal=Sum("subtotal_amount"),
            final_amount=Sum("final_amount"),
        )

        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "discount_count": campaign.discounts.count(),
            "redemptions": totals["redemptions"] or 0,
            "discount_given": totals["discount_given"] or 0,
            "subtotal_amount": totals["subtotal"] or 0,
            "final_amount": totals["final_amount"] or 0,
        }

    @staticmethod
    def list_campaign_performance(*, website):
        """
        Return campaign performance rows for dashboards.
        """
        campaigns = (
            website.discount_campaigns.all()
            .prefetch_related("discounts")
        )

        return [
            CampaignAnalyticsService.get_campaign_summary(
                campaign=campaign,
            )
            for campaign in campaigns
        ]