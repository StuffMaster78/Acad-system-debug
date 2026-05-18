from __future__ import annotations

from event_system.services.event_bus_service import (
    EventBusService,
)
from writer_compensation.events.reward_event_builder import (
    RewardIssuedEvent,
    RewardRevokedEvent,
)
from writer_compensation.events.reward_event_builder import (
    AchievementUnlockedEvent,
)


class RewardEventEmitter:
    """
    Emits reward domain events.
    """

    @staticmethod
    def reward_issued(
        *,
        reward,
    ) -> None:
        """
        Emit reward issued event.
        """

        event = RewardIssuedEvent(
            event_type="reward.issued",
            domain="writer_compensation",
            aggregate_id=str(reward.pk),
            actor_id=None,
            payload={
                "reward_id": str(reward.pk),
                "writer_id": str(
                    reward.writer_id,
                ),
                "website_id": str(
                    reward.website_id,
                ),
                "reward_rule_id": str(
                    reward.reward_rule_id,
                ),
                "reward_amount": str(
                    reward.reward_amount,
                ),
            },
        )

        EventBusService.publish(
            event=event,
        )

    @staticmethod
    def reward_revoked(
        *,
        reward,
    ) -> None:
        """
        Emit reward revoked event.
        """

        event = RewardRevokedEvent(
            event_type="reward.revoked",
            domain="writer_compensation",
            aggregate_id=str(reward.pk),
            actor_id=None,
            payload={
                "reward_id": str(reward.pk),
                "writer_id": str(
                    reward.writer_id,
                ),
            },
        )

        EventBusService.publish(
            event=event,
        )

    @staticmethod
    def achievement_unlocked(
        *,
        achievement,
    ) -> None:
        """
        Emit achievement unlocked event.
        """

        event = AchievementUnlockedEvent(
            event_type="achievement.unlocked",
            domain="writer_management",
            aggregate_id=str(
                achievement.pk,
            ),
            actor_id=None,
            payload={
                "achievement_id": str(
                    achievement.pk,
                ),
                "writer_id": str(
                    achievement.writer_id,
                ),
                "title": (
                    achievement.title
                ),
                "slug": (
                    achievement.slug
                ),
            },
        )

        EventBusService.publish(
            event=event,
        )