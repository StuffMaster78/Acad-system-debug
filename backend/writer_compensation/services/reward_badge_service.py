from __future__ import annotations


class RewardBadgeService:
    """
    Future-facing badge orchestration service.

    Today:
        stores metadata.

    Future:
        unlocks profile cosmetics,
        routing boosts,
        public ranking visuals,
        gamification systems.
    """

    @staticmethod
    def build_badge_payload(
        *,
        badge_name: str,
        reward_title: str,
    ) -> dict:
        return {
            "badge_name": badge_name,
            "reward_title": reward_title,
        }