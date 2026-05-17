from __future__ import annotations

from decimal import Decimal

from writer_compensation.enums.compensation_enums import (
    EventSource,
    EventType,
)
from writer_compensation.models.reward_rule import (
    RewardRule,
)
from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.event_intake_service import (
    EventIntakeService,
)


class RewardEventFactory:
    """
    Factory responsible for creating reward-related
    CompensationEvents.

    Centralizes:
        - titles
        - notes
        - idempotency
        - metadata semantics
    """

    @staticmethod
    def create_reward_event(
        *,
        reward: WriterReward,
        created_by=None,
    ):
        """
        Create financial event for a reward.
        """

        if reward.reward_amount <= Decimal("0.00"):
            return None

        rule = reward.reward_rule

        idempotency_key = (
            f"reward:{reward.pk}"
        )

        title = (
            reward.reward_title
            or rule.name
        )

        notes = (
            f"Reward issued via rule "
            f"{rule.slug}"
        )

        event, _ = EventIntakeService.record(
            website=reward.website,
            writer=reward.writer,
            event_type=EventType.PERFORMANCE_BONUS,
            amount=reward.reward_amount,
            source=EventSource.BONUS,
            title=title,
            notes=notes,
            source_type="writer_reward",
            source_id=reward.pk,
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        return event