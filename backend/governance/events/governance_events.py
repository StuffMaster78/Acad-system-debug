from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceEvent:
    event_type: str
    workflow_id: str
    node_id: str | None
    actor_id: int | None
    tenant_id: int
    payload: dict[str, Any]