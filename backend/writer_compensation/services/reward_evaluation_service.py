from __future__ import annotations

from django.db import transaction

from writer_compensation.models.reward_rule import RewardRule
from writer_compensation.services.reward_qualification_service import (
    RewardQualificationService,
)
from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.reward_duplicate_guard_service import (
    RewardDuplicateGuardService,
)
from writer_compensation.services.reward_fraud_detection_service import (
    RewardFraudDetectionService,
)
from writer_compensation.services.writer_reward_service import (
    WriterRewardService,
)
from reputation_system.services.writer_leaderboard_service import (
    WriterLeaderboardService,
)
from writer_compensation.services.reward_period_service import (
    RewardPeriodService,
)
from writer_compensation.services.reward_notification_service import (
    RewardNotificationService,
)

class RewardEvaluationService:
    """
    Evaluates reward rules against writers.

    Responsibilities:
        - iterate active rules
        - evaluate qualification
        - issue rewards

    NOT responsible for:
        - payout execution
        - ranking persistence
        - analytics
    """

    @classmethod
    @transaction.atomic
    def evaluate_writer(
        cls,
        *,
        website,
        writer,
        period_start=None,
        period_end=None,
        created_by=None,
    ) -> list:
        """
        Evaluate all active reward rules
        for a single writer.
        """

        issued_rewards = []

        rules = (
            RewardRule.objects
            .filter(
                website=website,
                is_active=True,
            )
            .order_by("id")
        )

        for rule in rules:
            qualification = (
                RewardQualificationService.evaluate(
                    writer=writer,
                    reward_rule=rule,
                )
            )

            if not qualification["qualified"]:
                continue

            reward = (
                WriterRewardService.issue_reward(
                    website=website,
                    writer=writer,
                    reward_rule=rule,
                    qualification_snapshot=(
                        qualification["snapshot"]
                    ),
                    period_start=period_start,
                    period_end=period_end,
                    created_by=created_by,
                )
            )

            issued_rewards.append(reward)

        return issued_rewards

    @classmethod
    @transaction.atomic
    def evaluate_many_writers(
        cls,
        *,
        website,
        writers,
        period_start=None,
        period_end=None,
        created_by=None,
    ) -> list:
        """
        Batch evaluation.

        Used for:
            - weekly rewards
            - monthly leaderboards
            - scheduled bonus jobs
        """

        all_rewards = []

        for writer in writers:
            rewards = cls.evaluate_writer(
                website=website,
                writer=writer,
                period_start=period_start,
                period_end=period_end,
                created_by=created_by,
            )

            all_rewards.extend(rewards)

        return all_rewards



    @classmethod
    def run_weekly_rewards(cls) -> None:
        """
        Execute weekly reward evaluation cycle.
        """

        period = RewardPeriodService.previous_week()

        rules = RewardRule.objects.filter(
            is_active=True,
            rule_type=RewardRule.RuleType.WEEKLY,
        )

        for rule in rules:
            cls.process_rule(
                rule=rule,
                period_start=period.start_date,
                period_end=period.end_date,
            )

    @classmethod
    def process_rule(
        cls,
        *,
        rule,
        period_start,
        period_end,
    ) -> None:
        """
        Evaluate a single reward rule.
        """

        leaderboard = (
            WriterLeaderboardService.global_leaderboard(
                limit=500,
            )
        )

        for entry in leaderboard:
            writer = entry.writer

            if RewardDuplicateGuardService.already_rewarded(
                writer=writer,
                reward_rule=rule,
                period_start=period_start,
                period_end=period_end,
            ):
                continue

            if RewardDuplicateGuardService.violates_cooldown(
                writer=writer,
                reward_rule=rule,
            ):
                continue

            fraud_result = (
                RewardFraudDetectionService.evaluate_writer(
                    writer_id=writer.pk,
                )
            )

            if not fraud_result.is_safe:
                continue

            qualification = (
                RewardQualificationService.evaluate(
                    writer=writer,
                    reward_rule=rule,
                )
            )

            if not qualification["qualified"]:
                continue

            reward = (
                WriterRewardService.issue_reward(
                    website=rule.website,
                    writer=writer,
                    reward_rule=rule,
                    qualification_snapshot=(
                        qualification["snapshot"]
                    ),
                    period_start=period_start,
                    period_end=period_end,
                )
            )

            RewardNotificationService.notify_reward_issued(
                    reward=reward,
                )