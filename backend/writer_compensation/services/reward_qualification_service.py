from __future__ import annotations

from decimal import Decimal

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from writer_compensation.models.reward_rule import RewardRule
from writer_compensation.selectors.writer_reward_selectors import (
    WriterRewardSelectors,
)
from reputation_system.services.reputation_query_service import (
    ReputationQueryService,
)

class RewardQualificationService:
    """
    Determines whether a writer qualifies
    for a specific reward rule.

    Pure evaluation layer.

    Responsibilities:
        - fetch qualification metrics
        - evaluate thresholds
        - build immutable qualification snapshot

    NOT responsible for:
        - issuing rewards
        - creating compensation events
        - payouts
    """

    @classmethod
    def evaluate(
        cls,
        *,
        writer,
        reward_rule: RewardRule,
    ) -> dict:
        """
        Evaluate writer qualification.
        Returns:
        {
            "qualified": bool,
            "snapshot": {...},
        }
        """

        reputation = (
            WriterReputationSnapshot.objects
            .filter(
                writer_id=writer.public_uuid,
            )
            .first()
        )

        snapshot = (
            ReputationQueryService
            .get_writer_reputation(
                writer_id=writer.id,
            )
        )

        if not snapshot:
            return {
                "qualified": False,
                "snapshot": {},
            }

        metadata = snapshot.metadata or {}

        qualification_snapshot = {
            "average_rating": snapshot.rating,
            "review_count": (
                snapshot.review_count
            ),
            "percentile_rank": Decimal(
                str(
                    metadata.get(
                        "percentile_rank",
                        "0.00",
                    )
                )
            ),
            "trust_score": Decimal(
                str(
                    metadata.get(
                        "trust_score",
                        "0.00",
                    )
                )
            ),
            "completed_orders": int(
                metadata.get(
                    "completed_orders",
                    0,
                )
            ),
            "composite_score": Decimal(
                str(
                    metadata.get(
                        "trust_score",
                        "0.00",
                    )
                )
            ),
        }

        average_rating = Decimal("0.00")
        review_count = 0

        if reputation:
            average_rating = reputation.rating
            review_count = reputation.review_count

        percentile_rank = cls._calculate_percentile_rank(
            writer=writer,
        )

        trust_score = cls._calculate_trust_score(
            writer=writer,
            average_rating=average_rating,
            review_count=review_count,
        )

        completed_orders = (
            cls._calculate_completed_orders(
                writer=writer,
            )
        )

        lateness_rate = cls._calculate_lateness_rate(
            writer=writer,
        )

        dispute_rate = cls._calculate_dispute_rate(
            writer=writer,
        )

        composite_score = cls._calculate_composite_score(
            average_rating=average_rating,
            percentile_rank=percentile_rank,
            trust_score=trust_score,
            completed_orders=completed_orders,
        )

        qualified = cls._passes_rule(
            reward_rule=reward_rule,
            average_rating=average_rating,
            review_count=review_count,
            percentile_rank=percentile_rank,
            trust_score=trust_score,
            completed_orders=completed_orders,
            lateness_rate=lateness_rate,
            dispute_rate=dispute_rate,
        )

        snapshot = {
            "average_rating": average_rating,
            "review_count": review_count,
            "percentile_rank": percentile_rank,
            "trust_score": trust_score,
            "completed_orders": completed_orders,
            "lateness_rate": lateness_rate,
            "dispute_rate": dispute_rate,
            "composite_score": composite_score,
        }

        return {
            "qualified": qualified,
            "snapshot": snapshot,
        }

    @staticmethod
    def _passes_rule(
        *,
        reward_rule: RewardRule,
        average_rating: Decimal,
        review_count: int,
        percentile_rank: Decimal,
        trust_score: Decimal,
        completed_orders: int,
        lateness_rate: Decimal,
        dispute_rate: Decimal,
    ) -> bool:
        """
        Declarative threshold evaluation.
        """

        if (
            reward_rule.minimum_avg_rating is not None
            and average_rating
            < reward_rule.minimum_avg_rating
        ):
            return False

        if (
            reward_rule.minimum_review_count is not None
            and review_count
            < reward_rule.minimum_review_count
        ):
            return False

        if (
            reward_rule.minimum_percentile_rank is not None
            and percentile_rank
            < reward_rule.minimum_percentile_rank
        ):
            return False

        if (
            reward_rule.minimum_trust_score is not None
            and trust_score
            < reward_rule.minimum_trust_score
        ):
            return False

        if (
            reward_rule.minimum_completed_orders
            is not None
            and completed_orders
            < reward_rule.minimum_completed_orders
        ):
            return False

        if (
            reward_rule.maximum_lateness_rate
            is not None
            and lateness_rate
            > reward_rule.maximum_lateness_rate
        ):
            return False

        if (
            reward_rule.maximum_dispute_rate
            is not None
            and dispute_rate
            > reward_rule.maximum_dispute_rate
        ):
            return False

        return True

    @staticmethod
    def _calculate_percentile_rank(
        *,
        writer,
    ) -> Decimal:
        """
        Placeholder percentile engine.

        Replace later with:
            - leaderboard engine
            - ranking engine
            - analytics warehouse
        """

        top_rewards_count = (
            WriterRewardSelectors
            .issued_rewards_for_writer(
                writer_id=writer.id,
            )
            .count()
        )

        if top_rewards_count >= 50:
            return Decimal("99.00")

        if top_rewards_count >= 20:
            return Decimal("92.00")

        if top_rewards_count >= 10:
            return Decimal("85.00")

        return Decimal("70.00")

    @staticmethod
    def _calculate_trust_score(
        *,
        writer,
        average_rating: Decimal,
        review_count: int,
    ) -> Decimal:
        """
        Simplified trust scoring model.

        Future inputs:
            - revision rates
            - lateness
            - disputes
            - fraud signals
            - client retention
            - refund ratios
        """

        base = average_rating * Decimal("20")

        review_bonus = min(
            Decimal(review_count) * Decimal("0.30"),
            Decimal("10.00"),
        )

        return min(
            base + review_bonus,
            Decimal("100.00"),
        )

    @staticmethod
    def _calculate_completed_orders(
        *,
        writer,
    ) -> int:
        """
        Placeholder.

        Replace with actual order aggregation.
        """

        return 25

    @staticmethod
    def _calculate_lateness_rate(
        *,
        writer,
    ) -> Decimal:
        """
        Placeholder lateness engine.
        """

        return Decimal("2.50")

    @staticmethod
    def _calculate_dispute_rate(
        *,
        writer,
    ) -> Decimal:
        """
        Placeholder dispute engine.
        """

        return Decimal("1.00")

    @staticmethod
    def _calculate_composite_score(
        *,
        average_rating: Decimal,
        percentile_rank: Decimal,
        trust_score: Decimal,
        completed_orders: int,
    ) -> Decimal:
        """
        Internal weighted ranking score.

        Purely for analytics/ranking snapshots.
        """

        return (
            (average_rating * Decimal("0.35"))
            + (percentile_rank * Decimal("0.25"))
            + (trust_score * Decimal("0.30"))
            + (
                Decimal(completed_orders)
                * Decimal("0.10")
            )
        )