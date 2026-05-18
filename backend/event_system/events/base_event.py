from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BaseDomainEvent:
    """
    Base immutable domain event.
    """

    event_type: str
    domain: str
    aggregate_id: str
    payload: dict[str, Any]
    actor_id: str | None = None