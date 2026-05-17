from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    """
    Output of governance decision engine.
    """

    allowed: bool
    requires_approval: bool
    blocked_reason: str | None = None

    risk_score: float = 0.0

    matched_policies: list[str] | None = None