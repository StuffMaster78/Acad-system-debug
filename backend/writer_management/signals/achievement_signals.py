from __future__ import annotations

from django.db.models.signals import (
    post_save,
)
from django.dispatch import receiver

from writer_management.models.writer_achievement import (
    WriterAchievement,
)
from writer_compensation.services.reward_event_emitter import (
    RewardEventEmitter,
)


@receiver(
    post_save,
    sender=WriterAchievement,
)
def achievement_created_signal(
    sender,
    instance: WriterAchievement,
    created: bool,
    **kwargs,
) -> None:
    """
    Emit achievement unlocked event.
    """

    if not created:
        return

    RewardEventEmitter.achievement_unlocked(
        achievement=instance,
    )