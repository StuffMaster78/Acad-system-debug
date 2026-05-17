from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)
from reputation_system.selectors.reputation_selectors import (
    ReputationSelectors,
)


class ReputationRebuildService:
    """
    A Safe Rebuild Engine
    Rebuilds reputation from scratch.

    Useful for:
        - partial rebuild
        - full target rebuild
        - batch-safe iteration
    """

    @classmethod
    def rebuild_target(cls, *, target_type: str, target_id: str) -> None:
        ReputationAggregationService._recalculate(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def rebuild_all_for_target_type(cls, target_type: str) -> None:
        target_ids = ReputationSelectors.distinct_target_ids(
            target_type=target_type
        )

        for target_id in target_ids:
            cls.rebuild_target(
                target_type=target_type,
                target_id=str(target_id),
            )