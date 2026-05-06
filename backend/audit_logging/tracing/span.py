from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Optional


@dataclass
class Span:
    name: str
    correlation_id: Optional[str] = None

    span_id: str = field(default_factory=lambda: __import__("uuid").uuid4().hex)

    start_ms: float = field(default_factory=lambda: time() * 1000)
    end_ms: float | None = None

    def finish(self) -> None:
        self.end_ms = time() * 1000

    def duration_ms(self) -> float | None:
        if self.end_ms is None:
            return None
        return self.end_ms - self.start_ms