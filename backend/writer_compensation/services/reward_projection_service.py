from __future__ import annotations

from decimal import Decimal

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from reputation_system.services.writer_leaderboard_service import (
    WriterLeaderboardService,
)
from writer_compensation.models.reward_rule import (
    RewardRule,
)
from writer_management.models.writer_performance import (
    WriterPerformanceMetrics,
)


class RewardProjectionService:
    """
    Predictive reward projection engine.

    Powers:
        - writer dashboards
        - gamification
        - milestone forecasting
        - reward eligibility previews
    """

    @classmethod
    def project_for_writer(
        cls,
        *,
        writer_id,
    ) -> dict:
        """
        Return projected reward insights.
        """

        snapshot = (
            WriterReputationSnapshot.objects
            .filter(
                writer_id=writer_id,
            )
            .first()
        )

        performance = (
            WriterPerformanceMetrics.objects
            .filter(
                writer_id=writer_id,
            )
            .first()
        )

        active_rules = (
            RewardRule.objects
            .filter(
                is_active=True,
            )
            .order_by("name")
        )

        percentile_rank = (
            WriterLeaderboardService
            .percentile_rank(
                writer_id=writer_id,
            )
        )

        projected_rewards = []

        for rule in active_rules:
            review_count = (
                snapshot.review_count
                if snapshot is not None
                else 0
            )

            minimum_review_count = (
                rule.minimum_review_count
                or 0
            )

            missing_reviews = max(
                0,
                (
                    minimum_review_count
                    - review_count
                ),
            )

            projected_rewards.append(
                {
                    "rule_name": rule.name,
                    "reward_amount": str(
                        rule.reward_amount
                    ),
                    "eligible_now": (
                        cls._eligible_now(
                            snapshot=snapshot,
                            performance=performance,
                            rule=rule,
                        )
                    ),
                    "missing_reviews": (
                        missing_reviews
                    ),
                }
            )

        projected_bonus = (
            cls._project_bonus(
                percentile_rank=(
                    percentile_rank
                ),
            )
        )

        return {
            "writer_id": writer_id,
            "trust_score": str(
                getattr(
                    snapshot,
                    "trust_score",
                    Decimal("0.00"),
                )
            ),
            "rating": str(
                getattr(
                    snapshot,
                    "rating",
                    Decimal("0.00"),
                )
            ),
            "review_count": getattr(
                snapshot,
                "review_count",
                0,
            ),
            "percentile_rank": (
                percentile_rank
            ),
            "projected_bonus": str(
                projected_bonus
            ),
            "next_milestone": (
                cls._next_milestone(
                    percentile_rank=(
                        percentile_rank
                    ),
                )
            ),
            "projected_rewards": (
                projected_rewards
            ),
        }

    @staticmethod
    def _eligible_now(
        *,
        snapshot,
        performance,
        rule,
    ) -> bool:
        """
        Lightweight eligibility estimation.
        """

        if snapshot is None:
            return False

        minimum_rating = getattr(
            rule,
            "minimum_rating",
            Decimal("0.00"),
        )

        minimum_review_count = getattr(
            rule,
            "minimum_review_count",
            0,
        )

        if snapshot.rating < minimum_rating:
            return False

        if (
            snapshot.review_count
            < minimum_review_count
        ):
            return False

        return True

    @staticmethod
    def _project_bonus(
        *,
        percentile_rank,
    ) -> Decimal:
        """
        Estimate likely upcoming bonus.
        """

        if percentile_rank is None:
            return Decimal("0.00")

        if percentile_rank >= 95:
            return Decimal("100.00")

        if percentile_rank >= 90:
            return Decimal("50.00")

        if percentile_rank >= 80:
            return Decimal("20.00")

        return Decimal("0.00")

    @staticmethod
    def _next_milestone(
        *,
        percentile_rank,
    ) -> str:
        """
        Return progression guidance.
        """

        if percentile_rank is None:
            return (
                "Complete more verified orders."
            )

        if percentile_rank >= 95:
            return (
                "Elite reward tier unlocked."
            )

        if percentile_rank >= 90:
            return (
                "Top 5% tier within reach."
            )

        if percentile_rank >= 80:
            return (
                "Maintain consistency to climb."
            )

        return (
            "Improve quality and review volume."
        )