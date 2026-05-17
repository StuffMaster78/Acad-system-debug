from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)
from writer_management.models.writer_profile import (
    WriterProfile,
)


@dataclass(frozen=True)
class LeaderboardEntry:
    """
    Immutable leaderboard row.
    """

    writer: WriterProfile
    rating: Decimal
    review_count: int
    percentile_rank: Decimal
    trust_score: Decimal
    completed_orders: int
    leaderboard_position: int


class WriterLeaderboardService:
    """
    Read-only leaderboard intelligence layer.

    Powers:
        - reward qualification
        - dashboards
        - ranking systems
        - competitions
        - adaptive routing
    """

    @classmethod
    def global_leaderboard(
        cls,
        *,
        limit: int = 100,
    ) -> list[LeaderboardEntry]:
        """
        Return ranked leaderboard entries.
        """

        snapshots = list(
            WriterReputationSnapshot.objects
            .select_related(None)
            .order_by(
                "-rating",
                "-review_count",
            )[:limit]
        )

        total = len(snapshots)

        entries: list[LeaderboardEntry] = []

        writer_ids = [
            snapshot.writer_id
            for snapshot in snapshots
        ]

        writers = {
            writer.pk: writer
            for writer in (
                WriterProfile.objects
                .filter(id__in=writer_ids)
            )
        }

        for index, snapshot in enumerate(snapshots):
            writer = writers.get(snapshot.writer_id)

            if not writer:
                continue

            metadata = snapshot.metadata or {}

            percentile = Decimal(
                str(
                    metadata.get(
                        "percentile_rank",
                        "0.00",
                    )
                )
            )

            trust_score = Decimal(
                str(
                    metadata.get(
                        "trust_score",
                        "0.00",
                    )
                )
            )

            completed_orders = int(
                metadata.get(
                    "completed_orders",
                    0,
                )
            )

            entries.append(
                LeaderboardEntry(
                    writer=writer,
                    rating=snapshot.rating,
                    review_count=(
                        snapshot.review_count
                    ),
                    percentile_rank=percentile,
                    trust_score=trust_score,
                    completed_orders=(
                        completed_orders
                    ),
                    leaderboard_position=(
                        index + 1
                    ),
                )
            )

        return entries

    @classmethod
    def writer_rank(
        cls,
        *,
        writer_id,
    ) -> int | None:
        """
        Return 1-indexed rank.
        """

        snapshots = list(
            WriterReputationSnapshot.objects
            .order_by(
                "-rating",
                "-review_count",
            )
            .values_list(
                "writer_id",
                flat=True,
            )
        )

        try:
            return (
                snapshots.index(writer_id)
                + 1
            )
        except ValueError:
            return None

    @classmethod
    def percentile_rank(
        cls,
        *,
        writer_id,
    ) -> Decimal | None:
        """
        Return percentile rank.
        """

        snapshots = list(
            WriterReputationSnapshot.objects
            .order_by(
                "-rating",
                "-review_count",
            )
            .values_list(
                "writer_id",
                flat=True,
            )
        )

        total = len(snapshots)

        if total == 0:
            return None

        try:
            rank = (
                snapshots.index(writer_id)
                + 1
            )
        except ValueError:
            return None

        percentile = (
            ((total - rank) / total)
            * 100
        )

        return Decimal(
            str(
                round(percentile, 2)
            )
        )