from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Command:
    """
    Canonical governance command.

    Everything entering the system is normalized into this shape.
    """

    command_type: str
    actor_id: int
    tenant_id: int

    payload: dict[str, Any]

    correlation_id: str | None = None
    idempotency_key: str | None = None

    source: str = "api"