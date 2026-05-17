from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional


EventType = Literal[
    "approval.node.started",
    "approval.node.approved",
    "approval.node.rejected",
    "approval.node.failed",
    "command.blocked",
    "command.executed",
]


@dataclass(frozen=True)
class GovernanceEventContract:
    """
    Immutable event contract for the entire governance system.

    This is the ONLY valid event shape emitted across:
    - approvals
    - commands
    - policies
    - audit system
    - event bus
    """

    event_type: EventType

    workflow_id: str | None = None
    command_id: str | None = None

    node_id: str | None = None

    actor_id: int | None = None
    tenant_id: int | None = None

    correlation_id: str | None = None

    payload: dict[str, Any] | None = None