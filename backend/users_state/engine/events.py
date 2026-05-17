from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StateEvent:
    """
    Base state event emitted after transitions.
    """
    user_id: int
    website_id: Optional[int]
    action: str
    reason: str


@dataclass(frozen=True)
class UserSuspended(StateEvent):
    pass


@dataclass(frozen=True)
class UserBlacklisted(StateEvent):
    pass


@dataclass(frozen=True)
class UserProbationStarted(StateEvent):
    pass