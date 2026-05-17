from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from writer_management.models.writer_performance import (
    WriterPerformanceMetrics,
)


class TrustScoreCalculationService:
    """
    Central trust score computation engine.

    This service transforms:
        - ratings
        - reviews
        - disputes
        - revisions
        - consistency
        - percentile ranking

    into a normalized marketplace trust score.

    IMPORTANT
    ----------
    This is NOT financial logic.
    This service never creates bonuses or compensation events.

    It only computes trust state.
    """

    # -------------------------------------------------------------
    # WEIGHT CONFIGURATION
    # Keep centralized and explicit.
    # -------------------------------------------------------------

    RATING_WEIGHT = Decimal("0.40")
    CONSISTENCY_WEIGHT = Decimal("0.20")
    PERCENTILE_WEIGHT = Decimal("0.20")
    VERIFIED_REVIEW_WEIGHT = Decimal("0.10")
    VELOCITY_WEIGHT = Decimal("0.10")

    # Penalties
    DISPUTE_PENALTY_MULTIPLIER = Decimal("25.00")
    REVISION_PENALTY_MULTIPLIER = Decimal("10.00")
    CANCELLATION_PENALTY_MULTIPLIER = Decimal("15.00")

    MAX_SCORE = Decimal("100.00")

    @classmethod
    def calculate_for_writer(
        cls,
        *,
        reputation_snapshot: WriterReputationSnapshot,
        performance_metrics: WriterPerformanceMetrics | None,
    ) -> Decimal:
        """
        Compute normalized trust score for a writer.
        """

        rating_component = cls._rating_component(
            rating=reputation_snapshot.rating,
        )

        consistency_component = cls._consistency_component(
            performance_metrics=performance_metrics,
        )

        percentile_component = cls._percentile_component(
            percentile_rank=reputation_snapshot.percentile_rank,
        )

        verified_review_component = (
            cls._verified_review_component(
                review_count=reputation_snapshot.review_count,
                verified_review_count=(
                    reputation_snapshot.verified_review_count
                ),
            )
        )

        velocity_component = cls._velocity_component(
            rating_velocity=reputation_snapshot.rating_velocity,
        )

        penalty_score = cls._penalty_score(
            performance_metrics=performance_metrics,
        )

        raw_score = (
            rating_component
            + consistency_component
            + percentile_component
            + verified_review_component
            + velocity_component
            - penalty_score
        )

        normalized = max(
            Decimal("0.00"),
            min(raw_score, cls.MAX_SCORE),
        )

        return normalized.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    # -------------------------------------------------------------
    # COMPONENTS
    # -------------------------------------------------------------

    @classmethod
    def _rating_component(
        cls,
        *,
        rating: Decimal,
    ) -> Decimal:
        """
        Rating normalized to 100 scale.
        """

        normalized = (rating / Decimal("5.00")) * Decimal("100.00")

        return normalized * cls.RATING_WEIGHT

    @classmethod
    def _consistency_component(
        cls,
        *,
        performance_metrics: WriterPerformanceMetrics | None,
    ) -> Decimal:
        """
        Rewards low revision/dispute/lateness rates.
        """

        if performance_metrics is None:
            return Decimal("0.00")

        quality_loss = (
            performance_metrics.revision_rate
            + performance_metrics.dispute_rate
            + performance_metrics.lateness_rate
        ) / Decimal("3.00")

        consistency = max(
            Decimal("0.00"),
            Decimal("100.00") - quality_loss,
        )

        return consistency * cls.CONSISTENCY_WEIGHT

    @classmethod
    def _percentile_component(
        cls,
        *,
        percentile_rank: Decimal,
    ) -> Decimal:
        """
        Direct percentile contribution.
        """

        return percentile_rank * cls.PERCENTILE_WEIGHT

    @classmethod
    def _verified_review_component(
        cls,
        *,
        review_count: int,
        verified_review_count: int,
    ) -> Decimal:
        """
        Protects against low-trust review spam.
        """

        if review_count <= 0:
            return Decimal("0.00")

        ratio = (
            Decimal(verified_review_count)
            / Decimal(review_count)
        ) * Decimal("100.00")

        return ratio * cls.VERIFIED_REVIEW_WEIGHT

    @classmethod
    def _velocity_component(
        cls,
        *,
        rating_velocity: Decimal,
    ) -> Decimal:
        """
        Positive recent momentum.
        """

        bounded = max(
            Decimal("0.00"),
            min(rating_velocity, Decimal("100.00")),
        )

        return bounded * cls.VELOCITY_WEIGHT

    # -------------------------------------------------------------
    # PENALTIES
    # -------------------------------------------------------------

    @classmethod
    def _penalty_score(
        cls,
        *,
        performance_metrics: WriterPerformanceMetrics | None,
    ) -> Decimal:
        """
        Risk deductions.
        """

        if performance_metrics is None:
            return Decimal("0.00")

        dispute_penalty = (
            performance_metrics.dispute_rate
            / Decimal("100.00")
        ) * cls.DISPUTE_PENALTY_MULTIPLIER

        revision_penalty = (
            performance_metrics.revision_rate
            / Decimal("100.00")
        ) * cls.REVISION_PENALTY_MULTIPLIER

        cancellation_penalty = (
            performance_metrics.cancellation_rate
            / Decimal("100.00")
        ) * cls.CANCELLATION_PENALTY_MULTIPLIER

        return (
            dispute_penalty
            + revision_penalty
            + cancellation_penalty
        )