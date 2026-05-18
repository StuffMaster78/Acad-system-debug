from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RolloutRule:
    attribute: str
    operator: str
    value: Any