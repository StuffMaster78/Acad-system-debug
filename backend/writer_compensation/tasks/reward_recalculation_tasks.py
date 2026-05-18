from __future__ import annotations

from celery import shared_task

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)


@shared_task(
    bind=True,
    max_retries=3,
)
def run_weekly_reward_cycle(
    self,
) -> None:
    """
    Execute weekly rewards.
    """

    RewardEvaluationOrchestrator(
    ).run_weekly_rewards()


@shared_task(
    bind=True,
    max_retries=3,
)
def run_monthly_reward_cycle(
    self,
) -> None:
    """
    Execute monthly rewards.
    """

    RewardEvaluationOrchestrator(
    ).run_monthly_rewards()