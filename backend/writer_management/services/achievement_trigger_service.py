from __future__ import annotations

from writer_management.services.achievement_service import (
    AchievementService,
)


class AchievementTriggerService:
    """
    Event-driven achievement automation.
    """

    @classmethod
    def process_order_completed(
        cls,
        *,
        writer,
    ) -> None:
        """
        Evaluate completion achievements.
        """

        AchievementService.evaluate_writer(
            writer=writer,
            website=website,
        )

    @classmethod
    def process_review_created(
        cls,
        *,
        writer,
    ) -> None:
        """
        Evaluate review achievements.
        """

        AchievementService.evaluate_writer(
            writer=writer,
            website=website,
        )

    @classmethod
    def process_reward_issued(
        cls,
        *,
        writer,
    ) -> None:
        """
        Evaluate reward milestones.
        """

        AchievementService.evaluate_writer(
            writer=writer,
            website=website,
        )