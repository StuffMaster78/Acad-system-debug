import uuid

from reputation_system.models.reputation_event import ReputationEvent
from reputation_system.domain.target_type_weights import TargetTypeWeights


class ReputationEventService:
    """
    Handles creation of reputation domain events.
    """

    @staticmethod
    def emit_recalculated(
        *,
        target_type: str,
        target_id: str,
        score,
        raw_score,
        count: int,
    ) -> ReputationEvent:

        event = ReputationEvent.objects.create(
            id=uuid.uuid4(),
            event_type=ReputationEvent.EventType.REPUTATION_RECALCULATED,
            target_type=target_type,
            target_id=target_id,
            payload={
                "score": str(score),
                "raw_score": str(raw_score),
                "weight": str(
                    TargetTypeWeights.get(target_type)
                ),
                "count": count,
            },
        )

        return event