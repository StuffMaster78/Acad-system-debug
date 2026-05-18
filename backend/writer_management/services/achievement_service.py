# writer_management/services/achievement_service.py

from __future__ import annotations

from decimal import Decimal

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from writer_management.models.writer_achievement import (
    WriterAchievement,
)
from writer_management.models.writer_performance import (
    WriterPerformanceMetrics,
)


class AchievementService:
    """
    Central writer achievement engine.

    Responsibilities:
        - achievement evaluation
        - milestone issuance
        - duplicate prevention
        - gamification progression
    """

    @classmethod
    def evaluate_writer(
        cls,
        *,
        writer,
        website,
    ) -> list[WriterAchievement]:
        """
        Evaluate all achievement paths.
        """

        achievements = []

        snapshot = (
            WriterReputationSnapshot.objects
            .filter(
                writer=writer,
            )
            .first()
        )

        performance = (
            WriterPerformanceMetrics.objects
            .filter(
                writer=writer,
            )
            .first()
        )

        if snapshot is None:
            return achievements

        quality = cls._quality_master(
            writer=writer,
            website=website,
            snapshot=snapshot,
        )

        if quality:
            achievements.append(
                quality,
            )

        consistency = cls._consistency_master(
            writer=writer,
            website=website,
            performance=performance,
        )

        if consistency:
            achievements.append(
                consistency,
            )

        milestone = cls._milestone_master(
            writer=writer,
            website=website,
            performance=performance,
        )

        if milestone:
            achievements.append(
                milestone,
            )

        return achievements

    @classmethod
    def _quality_master(
        cls,
        *,
        writer,
        website,
        snapshot,
    ) -> WriterAchievement | None:
        """
        Elite quality achievement.
        """

        if (
            snapshot.rating
            < Decimal("4.80")
        ):
            return None

        return cls._issue(
            writer=writer,
            website=website,
            slug="elite_quality_writer",
            achievement_type=(
                WriterAchievement
                .AchievementType
                .QUALITY
            ),
            title="Elite Quality Writer",
            description=(
                "Maintained elite rating standards."
            ),
            badge_name="Elite Gold",
            points=500,
        )

    @classmethod
    def _consistency_master(
        cls,
        *,
        writer,
        website,
        performance,
    ) -> WriterAchievement | None:
        """
        Consistency achievement.
        """

        if performance is None:
            return None

        if (
            performance.lateness_rate
            > Decimal("1.00")
        ):
            return None

        return cls._issue(
            writer=writer,
            website=website,
            slug="deadline_guardian",
            achievement_type=(
                WriterAchievement
                .AchievementType
                .CONSISTENCY
            ),
            title="Deadline Guardian",
            description=(
                "Maintained extremely low lateness."
            ),
            badge_name="Guardian",
            points=350,
        )

    @classmethod
    def _milestone_master(
        cls,
        *,
        writer,
        website,
        performance,
    ) -> WriterAchievement | None:
        """
        Milestone achievement.
        """

        if performance is None:
            return None

        if (
            performance.completed_orders
            < 100
        ):
            return None

        return cls._issue(
            writer=writer,
            website=website,
            slug="hundred_orders",
            achievement_type=(
                WriterAchievement
                .AchievementType
                .MILESTONE
            ),
            title="100 Orders Completed",
            description=(
                "Completed 100 successful orders."
            ),
            badge_name="Centurion",
            points=750,
        )

    @classmethod
    def _issue(
        cls,
        *,
        writer,
        website,
        slug,
        achievement_type,
        title,
        description,
        badge_name,
        points,
    ) -> WriterAchievement | None:
        """
        Persist achievement safely.
        """

        exists = (
            WriterAchievement.objects
            .filter(
                writer=writer,
                slug=slug,
            )
            .exists()
        )

        if exists:
            return None

        return (
            WriterAchievement.objects
            .create(
                website=website,
                writer=writer,
                slug=slug,
                achievement_type=(
                    achievement_type
                ),
                title=title,
                description=description,
                badge_name=badge_name,
                points=points,
            )
        )