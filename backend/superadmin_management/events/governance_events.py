from dataclasses import dataclass
from typing import Any


@dataclass
class UserCreatedEvent:
    user_id: int
    role: str
    website_id: int | None
    temp_password: str


@dataclass
class UserSuspendedEvent:
    user_id: int
    reason: str
    duration_days: int | None


@dataclass
class UserBlacklistedEvent:
    user_id: int
    reason: str