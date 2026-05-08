from dataclasses import dataclass, field
import uuid
import time
from typing import Optional


@dataclass
class Span:
    name: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    parent_id: Optional[str] = None

    start_time: float = field(default_factory=lambda: time.time())
    end_time: Optional[float] = None

    def finish(self) -> None:
        self.end_time = time.time()

    def duration_ms(self) -> Optional[float]:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000