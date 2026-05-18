from __future__ import annotations

import logging

from celery import shared_task

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def run_weekly_rewards_task(self) -> None:
    """
    Execute weekly reward cycle.
    """

    logger.info(
        "Starting weekly reward evaluation task.",
    )

    RewardEvaluationOrchestrator.run_weekly_rewards()

    logger.info(
        "Completed weekly reward evaluation task.",
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def run_monthly_rewards_task(self) -> None:
    """
    Execute monthly reward cycle.
    """

    logger.info(
        "Starting monthly reward evaluation task.",
    )

    RewardEvaluationOrchestrator.run_monthly_rewards()

    logger.info(
        "Completed monthly reward evaluation task.",
    )