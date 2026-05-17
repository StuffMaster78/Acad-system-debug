from typing import Protocol, Optional


class GovernanceUser(Protocol):
    id: int
    role: str
    is_suspended: bool
    suspension_reason: Optional[str]
    is_blacklisted: bool
    is_on_probation: bool