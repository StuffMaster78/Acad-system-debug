from __future__ import annotations

import logging

from django.db import transaction

from writer_compensation.models.reward_rule import (
    RewardRule,
)
from writer_compensation.services.reward_evaluation_service import (
    RewardEvaluationService,
)
from writer_compensation.services.reward_period_service import (
    RewardPeriodService,
)

logger = logging.getLogger(__name__)


class RewardEvaluationOrchestrator:
    """
    Canonical reward orchestration layer.

    Responsibilities:
        - scheduled reward execution
        - event-driven reevaluation
        - batching
        - orchestration
        - logging

    NOT responsible for:
        - qualification rules
        - fraud scoring
        - reward persistence internals
    """

    @classmethod
    @transaction.atomic
    def run_weekly_rewards(cls) -> None:
        """
        Execute weekly reward cycle.
        """

        period = RewardPeriodService.previous_week()

        rules = (
            RewardRule.objects
            .filter(
                is_active=True,
                rule_type=RewardRule.RuleType.WEEKLY,
            )
            .select_related("website")
            .order_by("id")
        )

        for rule in rules:
            logger.info(
                "Running weekly reward rule=%s",
                rule.slug,
            )

            RewardEvaluationService.process_rule(
                rule=rule,
                period_start=period.start_date,
                period_end=period.end_date,
            )

    @classmethod
    @transaction.atomic
    def run_monthly_rewards(cls) -> None:
        """
        Execute monthly reward cycle.
        """

        period = RewardPeriodService.previous_month()

        rules = (
            RewardRule.objects
            .filter(
                is_active=True,
                rule_type=RewardRule.RuleType.MONTHLY,
            )
            .select_related("website")
            .order_by("id")
        )

        for rule in rules:
            logger.info(
                "Running monthly reward rule=%s",
                rule.slug,
            )

            RewardEvaluationService.process_rule(
                rule=rule,
                period_start=period.start_date,
                period_end=period.end_date,
            )

    @classmethod
    def handle_review_created(
        cls,
        *,
        review,
    ) -> None:
        """
        Trigger reactive reevaluation
        after review creation.
        """

        logger.info(
            "Review created reevaluation target=%s",
            review.target_id,
        )

        cls._run_realtime_target_refresh(
            website=review.website,
        )

    @classmethod
    def handle_review_approved(
        cls,
        *,
        review,
    ) -> None:
        """
        Trigger reevaluation after
        moderation approval.
        """

        logger.info(
            "Review approved reevaluation review=%s",
            review.pk,
        )

        cls._run_realtime_target_refresh(
            website=review.website,
        )

    @classmethod
    def handle_order_completed(
        cls,
        *,
        order,
    ) -> None:
        """
        Trigger reevaluation after
        successful order completion.
        """

        logger.info(
            "Order completed reevaluation order=%s",
            order.pk,
        )

        cls._run_realtime_target_refresh(
            website=order.website,
        )

    @classmethod
    def handle_writer_suspended(
        cls,
        *,
        writer,
    ) -> None:
        """
        Trigger trust recalculation after
        suspension.
        """

        logger.warning(
            "Writer suspended=%s",
            writer.pk,
        )

        cls._run_realtime_target_refresh(
            website=writer.account_profile.website,
        )

    @classmethod
    def _run_realtime_target_refresh(
        cls,
        *,
        website,
    ) -> None:
        """
        Lightweight reactive reevaluation.

        Intended for:
            - live ranking refresh
            - trust updates
            - incremental recalculation

        NOT intended for:
            - full weekly payouts
            - massive leaderboard sweeps
        """

        rules = (
            RewardRule.objects
            .filter(
                website=website,
                is_active=True,
            )
            .only(
                "id",
                "slug",
            )
        )

        logger.info(
            "Realtime reward refresh rules=%s website=%s",
            rules.count(),
            website.pk,
        )