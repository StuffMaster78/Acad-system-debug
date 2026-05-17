from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.utils import timezone

from reviews_system.models.review import Review
from reputation_system.services.reputation_query_service import (
    ReputationQueryService,
)

@dataclass(frozen=True)
class FraudCheckResult:
    """
    Immutable fraud evaluation result.
    """

    is_safe: bool
    risk_score: Decimal
    reasons: list[str]


class RewardFraudDetectionService:
    """
    Detects suspicious reward qualification behavior.

    Defensive layer against:
        - review farming
        - trust manipulation
        - reward abuse
    """

    MAX_REVIEWS_PER_DAY = 15
    MAX_TRUST_SCORE = Decimal("98.00")
    MAX_REVIEW_COUNT = 10000

    @classmethod
    def evaluate_writer(
        cls,
        *,
        writer_id,
    ) -> FraudCheckResult:
        """
        Evaluate writer fraud risk.
        """
        snapshot = (
            ReputationQueryService
            .get_writer_reputation(
                writer_id=writer_id,
            )
        )
        reasons: list[str] = []
        risk_score = Decimal("0.00")
        today = timezone.now()

        if not snapshot:
            return FraudCheckResult(
                is_safe=False,
                risk_score=risk_score,
                reasons=reasons,
            )
        
        metadata = snapshot.metadata or {}
        trust_score = Decimal(
            str(
                metadata.get(
                    "trust_score",
                    "0.00",
                )
            )
        )
        if trust_score > cls.MAX_TRUST_SCORE:
            return FraudCheckResult(
                is_safe=False,
                risk_score=risk_score,
                reasons=reasons,
            )

        if (
            snapshot.review_count
            > cls.MAX_REVIEW_COUNT
        ):
            return FraudCheckResult(
                is_safe=False,
                risk_score=risk_score,
                reasons=reasons,
            )
        
        recent_reviews = (
            Review.objects
            .filter(
                writer_id=writer_id,
                created_at__date=today.date(),
            )
            .count()
        )

        if recent_reviews > cls.MAX_REVIEWS_PER_DAY:
            reasons.append(
                "abnormally_high_review_velocity",
            )
            risk_score += Decimal("35.00")

        is_safe = risk_score < Decimal("50.00")

        return FraudCheckResult(
            is_safe=is_safe,
            risk_score=risk_score,
            reasons=reasons,
        )
        

        

        

        