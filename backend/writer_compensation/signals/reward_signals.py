from django.db.models.signals import post_save
from django.dispatch import receiver

from writer_compensation.models.writer_reward import (
    WriterReward,
)

from writer_compensation.services.reward_notification_service import (
    RewardNotificationService,
)


@receiver(
    post_save,
    sender=WriterReward,
)
def writer_reward_post_save(
    sender,
    reward: WriterReward,
    created: bool,
    **kwargs,
):
    """
    Fire notifications after reward issuance.
    """

    if not created:
        return

    if (
        reward.status
        == WriterReward.RewardStatus.ISSUED
    ):
        RewardNotificationService.notify_reward_issued(
            reward=reward,
        )