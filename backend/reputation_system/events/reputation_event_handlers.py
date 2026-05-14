from reputation_system.services.reputation_aggregation_service import (
    ReputationAggregationService,
)
from reputation_system.services.reputation_rebuild_service import (
    ReputationRebuildService,
)
from reputation_system.models.reputation_event import ReputationEvent


def handle_reputation_event(event: ReputationEvent) -> None:
    """
    Central dispatcher for reputation domain events.

    This is called by event_system consumers.
    It decides what action to take based on event type.
    """

    if event.event_type == (
        ReputationEvent.EventType.REVIEW_PROCESSED
    ):
        _handle_review_processed(event)
        return

    if event.event_type == (
        ReputationEvent.EventType.REVIEW_SHADOWED
    ):
        _handle_review_shadowed(event)
        return

    if event.event_type == (
        ReputationEvent.EventType.REVIEW_REJECTED
    ):
        _handle_review_rejected(event)
        return

    if event.event_type == (
        ReputationEvent.EventType.REPUTATION_RECALCULATED
    ):
        _handle_recalculated(event)
        return


def _handle_review_processed(event: ReputationEvent) -> None:
    """
    Trigger incremental recomputation.
    """

    ReputationAggregationService._recalculate(
        target_type=event.target_type,
        target_id=str(event.target_id),
    )


def _handle_review_shadowed(event: ReputationEvent) -> None:
    """
    Shadowing affects scoring distribution.
    """

    ReputationAggregationService._recalculate(
        target_type=event.target_type,
        target_id=str(event.target_id),
    )


def _handle_review_rejected(event: ReputationEvent) -> None:
    """
    Rejected reviews must be excluded from scoring.
    """

    ReputationAggregationService._recalculate(
        target_type=event.target_type,
        target_id=str(event.target_id),
    )


def _handle_recalculated(event: ReputationEvent) -> None:
    """
    Optional hook for downstream systems.

    Examples later:
        - writer_compensation bonus triggers
        - analytics pipeline updates
    """

    # Intentionally no-op for now
    # Keeps system extensible without coupling
    return