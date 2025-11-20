# notifications_system/delivery/result.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class DeliveryResult:
    success: bool
    message: str = ""
    meta: Optional[dict[str, Any]] = None