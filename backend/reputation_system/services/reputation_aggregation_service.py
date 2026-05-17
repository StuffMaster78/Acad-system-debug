from __future__ import annotations

import uuid
from decimal import Decimal
from decimal import ROUND_HALF_UP

from reputation_system.domain.target_type_weights import (
    TargetTypeWeights,
)
from reputation_system.models.reputation_event import (
    ReputationEvent,
)
from reputation_system.models.website_reputation_snapshot import (
    WebsiteReputationSnapshot,
)
from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from reputation_system.selectors.reputation_selectors import (
    ReputationSelectors,
)
from reputation_system.services.trust_score_calculation_service import (
    TrustScoreCalculationService,
)
from reputation_system.services.writer_leaderboard_service import (
    WriterLeaderboardService,
)
from writer_management.models.writer_performance import (
    WriterPerformanceMetrics,
)


class ReputationAggregationService:
    """
    Deterministic reputation aggregation engine.

    Pipeline:
        1. Fetch reviews
        2. Compute weighted score
        3. Persist snapshot
        4. Emit event
    """

    @classmethod
    def process_review_event(
        cls,
        *,
        review_id: str,
        target_type: str,
        target_id: str,
        actor_id: str | None,
    ) -> None:
        cls._recalculate(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def process_shadow_event(
        cls,
        *,
        review_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        cls._recalculate(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def process_rejection_event(
        cls,
        *,
        review_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        cls._recalculate(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def _recalculate(
        cls,
        *,
        target_type: str,
        target_id: str,
    ) -> None:
        reviews = list(
            ReputationSelectors.reviews_for_target(
                target_type=target_type,
                target_id=target_id,
            )
        )

        count = len(reviews)

        if count == 0:
            cls._persist(
                target_type=target_type,
                target_id=target_id,
                score=Decimal("0.00"),
                count=0,
                raw_score=Decimal("0.00"),
            )
            return

        score, raw_score = cls._compute_score(
            reviews=reviews,
            target_type=target_type,
        )

        cls._persist(
            target_type=target_type,
            target_id=target_id,
            score=score,
            count=count,
            raw_score=raw_score,
        )

    @staticmethod
    def _compute_score(
        *,
        reviews,
        target_type: str,
    ) -> tuple[Decimal, Decimal]:
        """
        Pure scoring logic.

        No DB calls.
        No side effects.
        """

        total = Decimal("0.00")

        for review in reviews:
            total += Decimal(str(review.rating))

        raw_avg = (
            total / Decimal(len(reviews))
        )

        weight = TargetTypeWeights.get(
            target_type,
        )

        final_score = raw_avg * weight

        return final_score, raw_avg

    @staticmethod
    def _persist(
        *,
        target_type: str,
        target_id: str,
        score: Decimal,
        count: int,
        raw_score: Decimal,
    ) -> None:
        metadata: dict = {}

        if target_type == "website":
            snapshot, _ = (
                WebsiteReputationSnapshot.objects
                .get_or_create(
                    website_id=target_id,
                )
            )

            snapshot.rating = score.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            snapshot.review_count = count
            snapshot.metadata = metadata

            snapshot.save()

        else:
            snapshot, _ = (
                WriterReputationSnapshot.objects
                .get_or_create(
                    writer_id=target_id,
                )
            )

            snapshot.rating = score.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

            snapshot.review_count = count

            leaderboard_position = (
                WriterLeaderboardService.writer_rank(
                    writer_id=target_id,
                )
            )

            percentile_rank = (
                WriterLeaderboardService.percentile_rank(
                    writer_id=target_id,
                )
            )

            performance_metrics = (
                WriterPerformanceMetrics.objects
                .filter(
                    writer_id=target_id,
                )
                .first()
            )

            snapshot.percentile_rank = Decimal(
                str(percentile_rank or 0),
            )

            trust_score = (
                TrustScoreCalculationService
                .calculate_for_writer(
                    reputation_snapshot=snapshot,
                    performance_metrics=(
                        performance_metrics
                    ),
                )
            )

            metadata = {
                "leaderboard_position": (
                    leaderboard_position
                ),
                "percentile_rank": str(
                    percentile_rank or 0,
                ),
                "trust_score": str(
                    trust_score,
                ),
                "completed_orders": (
                    getattr(
                        performance_metrics,
                        "completed_orders",
                        0,
                    )
                ),
                "lateness_rate": str(
                    getattr(
                        performance_metrics,
                        "lateness_rate",
                        Decimal("0.00"),
                    )
                ),
                "dispute_rate": str(
                    getattr(
                        performance_metrics,
                        "dispute_rate",
                        Decimal("0.00"),
                    )
                ),
                "revision_rate": str(
                    getattr(
                        performance_metrics,
                        "revision_rate",
                        Decimal("0.00"),
                    )
                ),
            }

            snapshot.metadata = metadata

            snapshot.save()

        ReputationEvent.objects.create(
            id=uuid.uuid4(),
            event_type=(
                ReputationEvent.EventType
                .REPUTATION_RECALCULATED
            ),
            target_type=target_type,
            target_id=target_id,
            payload={
                "score": str(
                    snapshot.rating,
                ),
                "raw_score": str(
                    raw_score,
                ),
                "weight": str(
                    TargetTypeWeights.get(
                        target_type,
                    )
                ),
                "count": count,
                "metadata": metadata,
            },
        )