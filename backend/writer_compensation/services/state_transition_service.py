from __future__ import annotations

from django.utils import timezone

from writer_compensation.models.financial_state_transition_log_models import (
    FinancialStateTransitionLog,
)


class StateTransitionService:
    """
    Handles all financial state transitions.
    """

    @staticmethod
    def transition(
        website,
        entity_type: str,
        entity_id: str,
        from_state: str,
        to_state: str,
        trigger: str,
        actor=None,
        reason: str = "",
        metadata: dict | None = None,
    ) -> FinancialStateTransitionLog:
        """
        Log a state transition.
        """
        return FinancialStateTransitionLog.objects.create(
            website=website,
            entity_type=entity_type,
            entity_id=str(entity_id),
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            actor=actor,
            reason=reason,
            metadata=metadata or {},
            created_at=timezone.now(),
        )