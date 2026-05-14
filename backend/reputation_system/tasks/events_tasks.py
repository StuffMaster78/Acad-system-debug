from reputation_system.services.reputation_event_service import (
    ReputationEventService,
)


def emit_reputation_recalculated_event(
    target_type: str,
    target_id: str,
    score,
    raw_score,
    count: int,
) -> None:
    """
    Async event emission wrapper.
    """

    ReputationEventService.emit_recalculated(
        target_type=target_type,
        target_id=target_id,
        score=score,
        raw_score=raw_score,
        count=count,
    )