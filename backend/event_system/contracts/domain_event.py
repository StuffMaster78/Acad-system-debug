from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
from uuid import uuid4

@dataclass(frozen=True)
class DomainEvent:
    """
    Canonical system event.

    Production rules:
    - MUST be JSON serializable
    - MUST NOT contain ORM objects
    - MUST NOT contain UUID objects (always str)
    - MUST NOT contain business logic
    """

    event_type: str
    aggregate_id: str
    aggregate_type: str
    actor_id: str | None
    payload: dict[str, Any]

    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)