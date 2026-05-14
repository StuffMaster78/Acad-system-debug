from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)
from reputation_system.services.reputation_rebuild_service import (
    ReputationRebuildService,
)


def recompute_target_reputation(
    target_type: str,
    target_id: str,
) -> None:
    """
    Celery-friendly task wrapper for incremental recomputation.
    """

    ReputationAggregationService._recalculate(
        target_type=target_type,
        target_id=target_id,
    )


def rebuild_target_reputation(
    target_type: str,
    target_id: str,
) -> None:
    """
    Celery-friendly full rebuild task.
    """

    ReputationRebuildService.rebuild_target(
        target_type=target_type,
        target_id=target_id,
    )