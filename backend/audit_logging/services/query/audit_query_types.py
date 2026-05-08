from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEventQuery:
    """
    Immutable query contract for AuditQueryService.

    RULES:
    - no mutation
    - no business logic
    - API-safe transport object
    """

    website_id: str | None = None

    actor_id: int | None = None

    action: str | None = None
    action_contains: str | None = None

    object_type: str | None = None
    object_id: str | None = None

    correlation_id: str | None = None
    span_id: str | None = None

    is_sensitive: bool | None = None

    status: str | None = None

    occurred_after: datetime | None = None
    occurred_before: datetime | None = None

    limit: int = 100

    def __post_init__(self):
        if self.limit <= 0:
            raise ValueError("limit must be positive")

        if self.limit > 500:
            raise ValueError("limit exceeds maximum allowed (500)")