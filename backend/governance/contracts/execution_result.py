from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutionResult:
    """
    Final execution output of a command.
    """

    success: bool

    command_type: str
    actor_id: int
    tenant_id: int

    result: dict[str, Any] | None = None

    error: str | None = None

    rollback_available: bool = False