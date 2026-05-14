from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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