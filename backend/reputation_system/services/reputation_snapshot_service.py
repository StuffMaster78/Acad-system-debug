from decimal import Decimal, ROUND_HALF_UP

from reputation_system.selectors.reputation_selectors import (
    ReputationSelectors,
)


class ReputationSnapshotService:
    """
    Responsible only for writing reputation snapshots.

    Keeps persistence logic separate from scoring logic.
    """

    @staticmethod
    def upsert_snapshot(
        *,
        target_type: str,
        target_id: str,
        score: Decimal,
        count: int,
    ):
        if target_type == "website":
            snapshot = ReputationSelectors.website_snapshot(
                website_id=target_id,
            )
        else:
            snapshot = ReputationSelectors.writer_snapshot(
                writer_id=target_id,
            )

        snapshot.rating = score.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        snapshot.review_count = count
        snapshot.save()

        return snapshot