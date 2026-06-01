from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class TipCreationContract:
    """
    Immutable input contract for creating a Tip.

    This is the ONLY allowed input shape into TipCreationService.

    It ensures:
    - no request mutation leaks into domain layer
    - idempotency safety is enforceable
    - consistent payload hashing
    """

    sender: Any
    receiver: Any

    gross_amount: Decimal

    source_type: str

    idempotency_key: str

    reason: str = ""

    currency: str = "USD"

    # attribution objects (IMPORTANT: NOT IDs)
    order: Any | None = None
    special_order: Any | None = None
    class_purchase: Any | None = None

    context_type: str = ""

    order_id: int | None = None
    special_order_id: int | None = None
    class_purchase_id: int | None = None

    metadata: dict[str, Any] | None = None

    # ------------------------------------------------------------ #
    # HELPERS (NOT BUSINESS LOGIC)
    # ------------------------------------------------------------ #

    def payload(self) -> dict[str, Any]:
        """
        Canonical payload used for idempotency hashing.

        IMPORTANT:
        - must remain stable across retries
        - must not include runtime-generated fields
        """

        return {
            "sender_id": getattr(self.sender, "id", None),
            "receiver_id": getattr(self.receiver, "id", None),
            "gross_amount": str(self.gross_amount),
            "source_type": self.source_type,
            "reason": self.reason,
            "context_type": self.context_type,
             "order_id": getattr(self.order, "id", None),
            "special_order_id": getattr(self.special_order, "id", None),
            "class_purchase_id": getattr(self.class_purchase, "id", None),
            "metadata": self.metadata or {},
        }