from __future__ import annotations

from dataclasses import dataclass
from governance.contracts.command import Command


@dataclass
class GovernanceContext:
    command: Command

    role: str | None = None
    risk_score: float = 0.0
    correlation_id: str | None = None
    ip_address: str | None = None