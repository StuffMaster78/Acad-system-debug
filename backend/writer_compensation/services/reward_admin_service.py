from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.reward_notification_service import (
    RewardNotificationService,
)


class RewardAdminService:
    """
    Admin moderation/service layer
    for WriterReward operations.
    """

    @staticmethod
    @transaction.atomic
    def revoke_reward(
        *,
        reward: WriterReward,
        revoked_by,
        reason: str,
    ) -> WriterReward:
        """
        Revoke previously issued reward.
        """

        reward.status = (
            WriterReward.RewardStatus.REVOKED
        )

        reward.revoked_at = timezone.now()

        reward.metadata["revoked_by_id"] = (
            revoked_by.pk
        )

        reward.metadata["revocation_reason"] = (
            reason
        )

        reward.save(
            update_fields=[
                "status",
                "revoked_at",
                "metadata",
            ]
        )

        RewardNotificationService.notify_reward_revoked(
            reward=reward,
            reason=reason,
        )

        return reward