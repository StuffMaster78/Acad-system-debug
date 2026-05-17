from __future__ import annotations

from django.db.models import QuerySet

from writer_compensation.models.writer_reward import (
    WriterReward,
)


class WriterRewardSelectors:
    """
    Read/query layer for WriterReward.

    NO business logic here.
    NO mutation here.
    """

    @staticmethod
    def for_writer(
        *,
        writer_id: int,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .filter(writer_id=writer_id)
            .select_related(
                "reward_rule",
                "compensation_event",
                "website",
            )
            .order_by("-issued_at")
        )

    @staticmethod
    def issued_rewards_for_writer(
        *,
        writer_id: int,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .filter(
                writer_id=writer_id,
                status=WriterReward.RewardStatus.ISSUED,
            )
            .select_related(
                "reward_rule",
                "compensation_event",
            )
            .order_by("-issued_at")
        )

    @staticmethod
    def pending_rewards() -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .filter(
                status=WriterReward.RewardStatus.PENDING,
            )
            .select_related(
                "writer",
                "reward_rule",
                "website",
            )
            .order_by("issued_at")
        )

    @staticmethod
    def reward_history(
        *,
        writer_id: int,
        limit: int = 50,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .filter(writer_id=writer_id)
            .select_related(
                "reward_rule",
            )
            .order_by("-issued_at")[:limit]
        )

    @staticmethod
    def exists_for_period(
        *,
        writer_id: int,
        reward_rule_id: int,
        period_start,
        period_end,
    ) -> bool:
        """
        Used to enforce non-repeatable rewards
        within a specific evaluation period.
        """

        return (
            WriterReward.objects
            .filter(
                writer_id=writer_id,
                reward_rule_id=reward_rule_id,
                period_start=period_start,
                period_end=period_end,
            )
            .exclude(
                status=WriterReward.RewardStatus.REVOKED,
            )
            .exists()
        )

    @staticmethod
    def top_rewarded_writers(
        *,
        limit: int = 50,
    ) -> QuerySet[WriterReward]:
        return (
            WriterReward.objects
            .filter(
                status=WriterReward.RewardStatus.ISSUED,
            )
            .select_related(
                "writer",
                "reward_rule",
            )
            .order_by(
                "-reward_amount",
                "-issued_at",
            )[:limit]
        )