from __future__ import annotations

from django.db.models.signals import (
    post_save,
)
from django.dispatch import receiver

from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.reward_event_emitter import (
    RewardEventEmitter,
)


@receiver(
    post_save,
    sender=WriterReward,
)
def reward_created_signal(
    sender,
    instance: WriterReward,
    created: bool,
    **kwargs,
) -> None:
    """
    Emit reward issued event.
    """

    if not created:
        return

    RewardEventEmitter.reward_issued(
        reward=instance,
    )