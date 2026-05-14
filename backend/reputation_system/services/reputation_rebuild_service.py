from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)
from reputation_system.selectors.reputation_selectors import (
    ReputationSelectors,
)


class ReputationRebuildService:
    """
    Rebuilds reputation from scratch.

    Useful for:
        - migrations
        - bug fixes
        - replay logic (future event sourcing)
    """

    @classmethod
    def rebuild_target(cls, *, target_type: str, target_id: str) -> None:
        ReputationAggregationService._recalculate(
            target_type=target_type,
            target_id=target_id,
        )

    @classmethod
    def rebuild_all_for_target_type(cls, target_type: str) -> None:
        reviews = ReputationSelectors.reviews_for_target(
            target_type=target_type,
            target_id=None,
        )

        target_ids = {
            str(r.target_id) for r in reviews
        }

        for target_id in target_ids:
            cls.rebuild_target(
                target_type=target_type,
                target_id=target_id,
            )