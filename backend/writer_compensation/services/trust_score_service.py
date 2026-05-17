from __future__ import annotations

from decimal import Decimal

from reputation_system.services.reputation_query_service import (
    ReputationQueryService,
)


class TrustScoreService:
    """
    Composite trust scoring engine.

    Future inputs:
        - ratings
        - lateness
        - disputes
        - refund rate
        - revision rate
        - fraud flags
        - payout reliability
        - client retention
    """

    @staticmethod
    def calculate_writer_trust_score(
        *,
        writer_id,
    ) -> Decimal:
        """
        Current simple implementation.

        Formula evolves over time.
        """

        reputation = (
            ReputationQueryService
            .get_writer_reputation(
                writer_id=writer_id,
            )
        )

        if reputation is None:
            return Decimal("0.00")

        base_score = (
            reputation.rating
            * Decimal("20")
        )

        if reputation.review_count >= 50:
            base_score += Decimal("5.00")

        if reputation.review_count >= 100:
            base_score += Decimal("5.00")

        return min(
            base_score,
            Decimal("100.00"),
        )