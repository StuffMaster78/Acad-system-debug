from __future__ import annotations

import uuid

from decimal import Decimal

from django.db import transaction

from writer_compensation.enums.compensation_enums import (
    EventSource,
    EventType,
)
from writer_compensation.models.reward_rule import RewardRule
from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.selectors.writer_reward_selectors import (
    WriterRewardSelectors,
)
from writer_compensation.services.event_intake_service import (
    EventIntakeService,
)
from event_system.models.event_outbox import (
    EventOutbox,
)

class WriterRewardService:
    """
    Central reward issuance orchestration layer.

    Responsibilities:
        - reward issuance
        - duplicate prevention
        - optional financial event creation
        - immutable snapshot creation

    NOT responsible for:
        - qualification evaluation
        - rankings
        - payout execution
    """

    @classmethod
    @transaction.atomic
    def issue_reward(
        cls,
        *,
        website,
        writer,
        reward_rule: RewardRule,
        qualification_snapshot: dict,
        period_start=None,
        period_end=None,
        created_by=None,
    ) -> WriterReward:
        """
        Issue reward to writer.

        qualification_snapshot example:
        {
            "average_rating": Decimal("4.92"),
            "percentile_rank": Decimal("96.20"),
            "trust_score": Decimal("91.50"),
            "completed_orders": 44,
            "review_count": 21,
            "composite_score": Decimal("88.44"),
        }
        """

        # -----------------------------------------------------
        # DUPLICATE PROTECTION
        # -----------------------------------------------------

        if not reward_rule.is_repeatable:
            already_exists = (
                WriterRewardSelectors.exists_for_period(
                    writer_id=writer.id,
                    reward_rule_id=reward_rule.pk,
                    period_start=period_start,
                    period_end=period_end,
                )
            )

            if already_exists:
                raise ValueError(
                    "Reward already issued for this period."
                )

        compensation_event = None

        # -----------------------------------------------------
        # OPTIONAL FINANCIAL EVENT
        # -----------------------------------------------------

        if reward_rule.reward_amount > Decimal("0.00"):
            compensation_event, _ = (
                EventIntakeService.record(
                    website=website,
                    writer=writer,
                    event_type=EventType.PERFORMANCE_BONUS,
                    amount=reward_rule.reward_amount,
                    source=EventSource.BONUS,
                    title=reward_rule.name,
                    notes=reward_rule.description,
                    created_by=created_by,
                    idempotency_key=(
                        f"reward:"
                        f"{reward_rule.pk}:"
                        f"{writer.id}:"
                        f"{period_start}:"
                        f"{period_end}"
                    ),
                )
            )

        # -----------------------------------------------------
        # CREATE REWARD RECORD
        # -----------------------------------------------------

        reward = WriterReward.objects.create(
            website=website,
            writer=writer,
            reward_rule=reward_rule,
            compensation_event=compensation_event,
            status=WriterReward.RewardStatus.ISSUED,

            # Qualification snapshot
            average_rating=qualification_snapshot.get(
                "average_rating"
            ),
            percentile_rank=qualification_snapshot.get(
                "percentile_rank"
            ),
            trust_score=qualification_snapshot.get(
                "trust_score"
            ),
            composite_score=qualification_snapshot.get(
                "composite_score"
            ),
            completed_orders=qualification_snapshot.get(
                "completed_orders",
                0,
            ),
            review_count=qualification_snapshot.get(
                "review_count",
                0,
            ),

            # Reward snapshot
            reward_amount=reward_rule.reward_amount,
            trust_score_bonus=(
                reward_rule.trust_score_bonus
            ),
            badge_name=reward_rule.badge_name,
            reward_title=reward_rule.name,
            reward_description=reward_rule.description,

            # Period context
            period_start=period_start,
            period_end=period_end,

            metadata={
                "reward_type": reward_rule.reward_type,
                "rule_slug": reward_rule.slug,
            },
        )

        EventOutbox.objects.create(
            event_type="reward.issued",
            domain="writer_compensation",
            routing_key="reward.issued",
            payload={
                "reward_id": str(reward.pk),
                "writer_id": str(writer.id),
                "reward_rule_id": str(
                    reward_rule.pk
                ),
            },
            idempotency_key=(
                f"reward-issued:{reward.pk}"
            ),
            correlation_id=uuid.uuid4(),
        )

        return reward

    @classmethod
    @transaction.atomic
    def revoke_reward(
        cls,
        *,
        reward: WriterReward,
        revoked_by=None,
        reason: str = "",
    ) -> WriterReward:
        """
        Revoke previously issued reward.

        IMPORTANT:
        Financial reversal is NOT automatic.
        That decision belongs to finance/admin policy.
        """

        if (
            reward.status
            == WriterReward.RewardStatus.REVOKED
        ):
            return reward

        reward.status = (
            WriterReward.RewardStatus.REVOKED
        )

        reward.metadata["revoked_reason"] = reason

        if revoked_by:
            reward.metadata["revoked_by_id"] = (
                revoked_by.id
            )

        from django.utils import timezone

        reward.revoked_at = timezone.now()

        reward.save(
            update_fields=[
                "status",
                "metadata",
                "revoked_at",
            ]
        )

        return reward