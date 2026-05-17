from __future__ import annotations

from django.db.models import QuerySet

from writer_compensation.models.reward_rule import (
    RewardRule,
)
from writer_compensation.models.writer_reward import (
    WriterReward,
)


class RewardAPISelectors:
    """
    API-focused reward selectors.
    """

    @staticmethod
    def active_rules(
        *,
        website_id,
    ) -> QuerySet[RewardRule]:
        return (
            RewardRule.objects
            .filter(
                website_id=website_id,
                is_active=True,
            )
            .order_by("name")
        )

    @staticmethod
    def rewards_for_writer(
        *,
        writer_id,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .select_related(
                "writer",
                "reward_rule",
                "website",
            )
            .filter(
                writer_id=writer_id,
            )
            .order_by("-issued_at")
        )

    @staticmethod
    def rewards_for_website(
        *,
        website_id,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .select_related(
                "writer",
                "reward_rule",
            )
            .filter(
                website_id=website_id,
            )
            .order_by("-issued_at")
        )
    
    @staticmethod
    def reward_queryset() -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .select_related(
                "writer",
                "reward_rule",
                "website",
            )
        )