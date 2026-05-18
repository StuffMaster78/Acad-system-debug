from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RolloutContext:
    user_id: int | None = None
    tenant_id: int | None = None
    website_id: int | None = None

    email: str | None = None
    country_code: str | None = None
    plan: str | None = None

    is_staff: bool = False
    is_beta_user: bool = False

    attributes: dict[str, Any] = field(default_factory=dict)