from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from writer_compensation.models.reward_analytics_snapshot import (
    RewardAnalyticsSnapshot,
)
from writer_compensation.models.writer_reward import (
    WriterReward,
)


class RewardAnalyticsSnapshotService:
    """
    Creates daily analytics snapshots.
    """

    @classmethod
    def generate_daily_snapshot(
        cls,
        *,
        website,
    ) -> RewardAnalyticsSnapshot:
        """
        Generate analytics snapshot.
        """

        today = timezone.now().date()

        rewards = (
            WriterReward.objects
            .filter(
                website=website,
                issued_at__date=today,
            )
        )

        total_bonus = Decimal("0.00")

        for reward in rewards:
            total_bonus += (
                reward.reward_amount
            )

        snapshot, _ = (
            RewardAnalyticsSnapshot.objects
            .update_or_create(
                website=website,
                snapshot_date=today,
                defaults={
                    "rewards_issued": (
                        rewards.count()
                    ),
                    "total_bonus_amount": (
                        total_bonus
                    ),
                },
            )
        )

        return snapshot