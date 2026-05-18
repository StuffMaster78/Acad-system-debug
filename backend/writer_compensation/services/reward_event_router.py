from __future__ import annotations

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)
from writer_management.services.achievement_trigger_service import (
    AchievementTriggerService,
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

        if event_type == "review.created":
            cls._handle_review_created(
                payload=payload,
            )

        elif event_type == "order.completed":
            cls._handle_order_completed(
                payload=payload,
            )

    @classmethod
    def _handle_review_created(
        cls,
        *,
        payload: dict,
    ) -> None:
        """
        Trigger reward recalculation.
        """

        writer = payload.get("writer")

        if writer is None:
            return

        AchievementTriggerService(
        ).process_review_created(
            writer=writer,
        )

    @classmethod
    def _handle_order_completed(
        cls,
        *,
        payload: dict,
    ) -> None:
        """
        Trigger achievement checks.
        """

        writer = payload.get("writer")

        if writer is None:
            return

        AchievementTriggerService(
        ).process_order_completed(
            writer=writer,
        )