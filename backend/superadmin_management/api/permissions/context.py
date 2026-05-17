from dataclasses import dataclass
from typing import Any


@dataclass
class PermissionContext:
    user_id: int
    tenant_id: int
    role: str

    command_type: str
    payload: dict[str, Any]

    ip_address: str | None = None
    risk_score: float = 0.0