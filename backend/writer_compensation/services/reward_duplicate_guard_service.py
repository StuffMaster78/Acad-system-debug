from __future__ import annotations

from django.utils import timezone

from writer_compensation.models.writer_reward import (
    WriterReward,
)


class RewardDuplicateGuardService:
    """
    Prevents duplicate reward issuance.

    Handles:
        - repeated scheduler runs
        - Celery retries
        - cooldown enforcement
        - reward spam prevention
    """

    @classmethod
    def already_rewarded(
        cls,
        *,
        writer,
        reward_rule,
        period_start,
        period_end,
    ) -> bool:
        """
        True if reward already exists for period.
        """

        return WriterReward.objects.filter(
            writer=writer,
            reward_rule=reward_rule,
            period_start=period_start,
            period_end=period_end,
        ).exists()

    @classmethod
    def violates_cooldown(
        cls,
        *,
        writer,
        reward_rule,
    ) -> bool:
        """
        Enforce cooldown_days restriction.
        """

        cooldown_days = reward_rule.cooldown_days

        if not cooldown_days:
            return False

        latest_reward = (
            WriterReward.objects
            .filter(
                writer=writer,
                reward_rule=reward_rule,
            )
            .order_by("-issued_at")
            .first()
        )

        if not latest_reward:
            return False

        elapsed = timezone.now() - latest_reward.issued_at

        return elapsed.days < cooldown_days

    @classmethod
    def exceeds_period_limit(
        cls,
        *,
        writer,
        reward_rule,
        period_start,
        period_end,
    ) -> bool:
        """
        Enforce max_rewards_per_period.
        """

        limit = reward_rule.max_rewards_per_period

        if not limit:
            return False

        count = (
            WriterReward.objects
            .filter(
                writer=writer,
                reward_rule=reward_rule,
                period_start=period_start,
                period_end=period_end,
            )
            .count()
        )

        return count >= limit