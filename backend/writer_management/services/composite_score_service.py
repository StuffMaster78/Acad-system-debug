"""
writer_management/services/composite_score_service.py

Computes a single weighted composite score from a writer's
performance metrics for a given period.

THE SCORE
---------
A number between 0 and 100.
Higher is better.
Used by:
    level_progression_service  — promotion/demotion decisions
    performance_aggregator     — weekly ranking/percentile
    reward_evaluation_service  — min_composite_score threshold

WEIGHTS (default — configurable per website in future)
-------
    avg_rating          40%   — client satisfaction (most important)
    completion_rate     25%   — reliability
    lateness_rate       15%   — time management (penalty — inverted)
    revision_rate       10%   — quality on first submission (penalty)
    dispute_rate         5%   — conflict rate (penalty)
    cancellation_rate    5%   — commitment (penalty)
                       ----
                       100%

Penalty components: raw value is subtracted from maximum.
    e.g. lateness_rate=20% → penalty_score = 15 * (1 - 0.20) = 12.0
    e.g. lateness_rate=0%  → penalty_score = 15 * (1 - 0.00) = 15.0

INPUTS
------
Accepts a WriterPerformanceSnapshot or a plain dict with the
same field names. This makes it testable without DB rows.

All rate inputs must be proportions (0.0–1.0) matching
WriterPerformanceSnapshot field conventions.
avg_rating must be on a 0–5 scale.

OUTPUTS
-------
Returns a Decimal between 0.00 and 100.00.
"""

import logging
from decimal import ROUND_HALF_UP, Decimal

logger = logging.getLogger(__name__)

# Default weights — must sum to Decimal("1.00")
DEFAULT_WEIGHTS = {
    "avg_rating":        Decimal("0.40"),
    "completion_rate":   Decimal("0.25"),
    "lateness_rate":     Decimal("0.15"),  # penalty
    "revision_rate":     Decimal("0.10"),  # penalty
    "dispute_rate":      Decimal("0.05"),  # penalty
    "cancellation_rate": Decimal("0.05"),  # penalty
}

MAX_RATING = Decimal("5.00")
SCORE_SCALE = Decimal("100")


class CompositeScoreService:

    @staticmethod
    def compute(snapshot, weights: dict | None = None) -> Decimal:
        """
        Compute composite score from a snapshot or dict.

        Args:
            snapshot: WriterPerformanceSnapshot instance or dict
                      with the same field names.
            weights:  Optional weight overrides. Must sum to 1.00.
                      Defaults to DEFAULT_WEIGHTS.

        Returns:
            Decimal between 0.00 and 100.00.
        """
        w = weights or DEFAULT_WEIGHTS

        # Extract values — handle both model instance and dict
        avg_rating        = CompositeScoreService._get(snapshot, "average_rating", Decimal("0"))
        completion_rate   = CompositeScoreService._get(snapshot, "completion_rate", Decimal("0"))
        lateness_rate     = CompositeScoreService._get(snapshot, "lateness_rate", Decimal("0"))
        revision_rate     = CompositeScoreService._get(snapshot, "revision_rate", Decimal("0"))
        dispute_rate      = CompositeScoreService._get(snapshot, "dispute_rate", Decimal("0"))
        cancellation_rate = CompositeScoreService._get(snapshot, "cancellation_rate", Decimal("0"))

        # Clamp all inputs to valid ranges
        avg_rating        = CompositeScoreService._clamp(avg_rating, Decimal("0"), MAX_RATING)
        completion_rate   = CompositeScoreService._clamp(completion_rate, Decimal("0"), Decimal("1"))
        lateness_rate     = CompositeScoreService._clamp(lateness_rate, Decimal("0"), Decimal("1"))
        revision_rate     = CompositeScoreService._clamp(revision_rate, Decimal("0"), Decimal("1"))
        dispute_rate      = CompositeScoreService._clamp(dispute_rate, Decimal("0"), Decimal("1"))
        cancellation_rate = CompositeScoreService._clamp(cancellation_rate, Decimal("0"), Decimal("1"))

        # Normalise rating to 0–1 scale
        rating_norm = avg_rating / MAX_RATING

        # Compute weighted component scores (all 0–1)
        rating_score      = rating_norm        * w["avg_rating"]
        completion_score  = completion_rate    * w["completion_rate"]
        # Penalties: invert the rate (higher rate = lower score)
        lateness_score    = (Decimal("1") - lateness_rate)     * w["lateness_rate"]
        revision_score    = (Decimal("1") - revision_rate)     * w["revision_rate"]
        dispute_score     = (Decimal("1") - dispute_rate)      * w["dispute_rate"]
        cancel_score      = (Decimal("1") - cancellation_rate) * w["cancellation_rate"]

        # Sum and scale to 0–100
        raw = (
            rating_score
            + completion_score
            + lateness_score
            + revision_score
            + dispute_score
            + cancel_score
        ) * SCORE_SCALE

        score = raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        logger.debug(
            "CompositeScore: rating=%.2f completion=%.4f lateness=%.4f "
            "revision=%.4f dispute=%.4f cancel=%.4f → score=%s",
            float(avg_rating),
            float(completion_rate),
            float(lateness_rate),
            float(revision_rate),
            float(dispute_rate),
            float(cancellation_rate),
            score,
        )

        return score

    @staticmethod
    def compute_and_save(snapshot) -> Decimal:
        """
        Compute composite score and write it back to the snapshot.
        Sets is_processed=True.

        Args:
            snapshot: WriterPerformanceSnapshot instance.

        Returns:
            Computed Decimal score.
        """
        score = CompositeScoreService.compute(snapshot)
        snapshot.composite_score = score
        snapshot.is_processed = True
        snapshot.save(update_fields=["composite_score", "is_processed"])
        return score

    @staticmethod
    def compute_percentile(
        writer_score: Decimal,
        all_scores: list[Decimal],
    ) -> Decimal:
        """
        Compute what percentage of writers this score beats.

        Args:
            writer_score: This writer's composite score.
            all_scores:   All composite scores for the same site/period.

        Returns:
            Decimal 0.00–100.00.
            100.00 = better than everyone.
            0.00 = lowest score.
        """
        if not all_scores:
            return Decimal("0.00")

        beaten = sum(1 for s in all_scores if writer_score > s)
        percentile = (Decimal(str(beaten)) / Decimal(str(len(all_scores)))) * SCORE_SCALE
        return percentile.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # ----------------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _get(source, field: str, default: Decimal) -> Decimal:
        """Extract a field from a model instance or dict."""
        if isinstance(source, dict):
            value = source.get(field, default)
        else:
            value = getattr(source, field, default)
        if value is None:
            return default
        return Decimal(str(value))

    @staticmethod
    def _clamp(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
        """Clamp a value to [minimum, maximum]."""
        return max(minimum, min(maximum, value))