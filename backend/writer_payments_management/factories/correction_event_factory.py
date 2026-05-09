from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.utils import timezone

from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.enums.financial_event_enums import (
    FinancialEventType,
    FinancialEventStatus,
)


class CorrectionEventFactory:
    """
    Factory responsible ONLY for creating correction FinancialEvents.

    Guarantees:
        - no updates to existing records
        - safe for retries (idempotency supported externally)
        - deterministic metadata payloads
    """

    @staticmethod
    def create(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        correction_type: str,
        source: str,
        created_by: Any | None = None,
        related_object: Any | None = None,
        idempotency_key: str | None = None,
    ) -> FinancialEvent:

        if amount == Decimal("0.00"):
            raise ValueError("Correction amount cannot be zero.")

        metadata: dict[str, Any] = {
            "system": "correction_event",
            "source": source,
            "correction_type": correction_type,
            "generated_at": timezone.now().isoformat(),
        }

        if idempotency_key:
            metadata["idempotency_key"] = idempotency_key

        if related_object is not None:
            obj_id = getattr(related_object, "id", None)
            metadata["related_object_id"] = obj_id
            metadata["related_object_type"] = related_object.__class__.__name__

        return FinancialEvent.objects.create(
            website=website,
            writer=writer,
            event_type=FinancialEventType.ADJUSTMENT,
            status=FinancialEventStatus.MATURED,
            amount=amount,
            title="Correction Event",
            description=reason,
            created_by=created_by,
            metadata=metadata,
        )