from __future__ import annotations

from django.db.models import Count
from django.db.models import Sum

from writer_compensation.models.writer_reward import (
    WriterReward,
)


class RewardAnalyticsService:
    """
    Analytics and reporting layer
    for reward systems.
    """

    @staticmethod
    def total_rewards_issued(
        *,
        website,
    ):
        return (
            WriterReward.objects
            .filter(
                website=website,
                status=WriterReward.RewardStatus.ISSUED,
            )
            .count()
        )

    @staticmethod
    def total_reward_amount(
        *,
        website,
    ):
        result = (
            WriterReward.objects
            .filter(
                website=website,
                status=WriterReward.RewardStatus.ISSUED,
            )
            .aggregate(
                total=Sum("reward_amount"),
            )
        )

        return result["total"] or 0

    @staticmethod
    def top_rewarded_writers(
        *,
        website,
        limit: int = 20,
    ):
        return (
            WriterReward.objects
            .filter(
                website=website,
                status=WriterReward.RewardStatus.ISSUED,
            )
            .values(
                "writer_id",
            )
            .annotate(
                total_rewards=Count("id"),
                total_amount=Sum("reward_amount"),
            )
            .order_by(
                "-total_amount",
            )[:limit]
        )

    @staticmethod
    def most_effective_reward_rules(
        *,
        website,
    ):
        """
        Future:
            correlate rewards with:
                - retention
                - writer activity
                - completion rates
                - revenue
        """

        return (
            WriterReward.objects
            .filter(
                website=website,
            )
            .values(
                "reward_rule__name",
            )
            .annotate(
                issued_count=Count("id"),
                total_amount=Sum("reward_amount"),
            )
            .order_by(
                "-issued_count",
            )
        )