from __future__ import annotations

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)


class RewardEventRouter:
    """
    Central reward-domain event mapper.
    """

    @classmethod
    def route(
        cls,
        *,
        event_type: str,
        payload: dict,
    ) -> None:
        """
        Route domain events.
        """

        if event_type in {
            "review.processed",
            "order.completed",
            "review.approved",
        }:
            RewardEvaluationOrchestrator.run_weekly_rewards()