from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

from governance.contracts.command import Command
from governance.approvals.dag.contracts.results import PolicyResult, ApprovalResult


@dataclass(frozen=True)
class GovernanceSnapshot:
    """
    Immutable snapshot of a governance decision point.

    This is your:
    - audit truth source
    - replay input
    - forensic debugging artifact
    - compliance record

    NEVER mutate after creation.
    """

    snapshot_id: str

    created_at: datetime

    command: Command

    policy_result: PolicyResult

    approval_result: Optional[ApprovalResult] = None

    context: dict[str, Any] | None = None

    system_metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Safe serialization for:
        - audit logs
        - event bus
        - storage (JSON fields)
        """

        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at.isoformat(),
            "command": asdict(self.command),
            "policy_result": asdict(self.policy_result),
            "approval_result": asdict(self.approval_result)
            if self.approval_result
            else None,
            "context": self.context or {},
            "system_metadata": self.system_metadata or {},
        }