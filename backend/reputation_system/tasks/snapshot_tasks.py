from decimal import Decimal
from reputation_system.services.reputation_snapshot_service import (
    ReputationSnapshotService,
)


def update_snapshot_task(
    target_type: str,
    target_id: str,
    score: float,
    count: int,
) -> None:
    """
    Async-safe snapshot update wrapper.
    """

    ReputationSnapshotService.upsert_snapshot(
        target_type=target_type,
        target_id=target_id,
        score=Decimal(str(score)),
        count=count,
    )