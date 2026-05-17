from __future__ import annotations

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)


class LeaderboardAPISelectors:
    """
    Leaderboard API selectors.
    """

    @staticmethod
    def global_leaderboard(
        *,
        limit: int = 100,
    ):
        return (
            WriterReputationSnapshot.objects
            .select_related("writer")
            .order_by(
                "-trust_score",
                "-rating",
                "-review_count",
            )[:limit]
        )