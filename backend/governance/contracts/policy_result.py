from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyResult:
    """
    Output of policy engine evaluation.
    """

    allowed: bool

    requires_approval: bool = False

    risk_score: float = 0.0

    matched_rules: list[str] | None = None

    reason: str | None = None