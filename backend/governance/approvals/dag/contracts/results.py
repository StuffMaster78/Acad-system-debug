from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Result:
    """
    Generic execution result.

    Used across:
    - CommandBus
    - Approval DAG
    - Policy engine
    - Governance execution layer
    """

    ok: bool
    status: str  # executed | blocked | pending | rejected | approved | failed

    data: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class CommandResult(Result):
    command_type: str | None = None
    command_id: str | None = None


@dataclass(frozen=True)
class ApprovalResult(Result):
    workflow_id: str | None = None
    node_id: str | None = None

    next_nodes: list[str] | None = None


@dataclass(frozen=True)
class PolicyResult:
    """
    Output of policy evaluation layer.
    """

    allowed: bool
    requires_approval: bool = False
    blocked_reason: str | None = None
    risk_score: float = 0.0