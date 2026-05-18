from __future__ import annotations

from dataclasses import dataclass

from event_system.events.base_event import (
    BaseDomainEvent,
)


@dataclass(slots=True)
class RewardIssuedEvent(
    BaseDomainEvent,
):
    """
    Reward issued domain event.
    """


@dataclass(slots=True)
class RewardRevokedEvent(
    BaseDomainEvent,
):
    """
    Reward revoked domain event.
    """

@dataclass(slots=True)
class AchievementUnlockedEvent(
    BaseDomainEvent,
):
    """
    Achievement unlocked event.
    """