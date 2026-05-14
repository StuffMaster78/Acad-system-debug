import uuid
from decimal import Decimal, ROUND_HALF_UP

from reputation_system.domain.target_type_weights import (
    TargetTypeWeights,
)
from reputation_system.models.reputation_event import ReputationEvent
from reputation_system.selectors.reputation_selectors import (
    ReputationSelectors,
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
        cls._recalculate(target_type, target_id)

    @classmethod
    def process_shadow_event(
        cls,
        *,
        review_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        cls._recalculate(target_type, target_id)

    @classmethod
    def process_rejection_event(
        cls,
        *,
        review_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        cls._recalculate(target_type, target_id)

    @classmethod
    def _recalculate(cls, target_type: str, target_id: str) -> None:
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
    def _compute_score(reviews, target_type: str):
        """
        Pure scoring logic:
            - no DB calls
            - no side effects
        """

        total = Decimal("0.00")

        for r in reviews:
            total += Decimal(str(r.rating))

        raw_avg = total / Decimal(len(reviews))

        weight = TargetTypeWeights.get(target_type)
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
        from reputation_system.models.website_reputation_snapshot import (
            WebsiteReputationSnapshot,
        )
        from reputation_system.models.writer_reputation_snapshot import (
            WriterReputationSnapshot,
        )

        if target_type == "website":
            snapshot, _ = WebsiteReputationSnapshot.objects.get_or_create(
                website_id=target_id,
            )
        else:
            snapshot, _ = WriterReputationSnapshot.objects.get_or_create(
                writer_id=target_id,
            )

        snapshot.rating = score.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        snapshot.review_count = count
        snapshot.save()

        ReputationEvent.objects.create(
            id=uuid.uuid4(),
            event_type=ReputationEvent.EventType.REPUTATION_RECALCULATED,
            target_type=target_type,
            target_id=target_id,
            payload={
                "score": str(snapshot.rating),
                "raw_score": str(raw_score),
                "weight": str(TargetTypeWeights.get(target_type)),
                "count": count,
            },
        )