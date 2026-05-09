from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_payments_management.enums.financial_event_enums import (
    FinancialEventStatus,
    FinancialEventType,
)

from writer_payments_management.models.financial_event_models import (
    FinancialEvent,
)

from writer_payments_management.services.outbox_service import (
    OutboxService,
)


class AdjustmentService:
    """
    Handles controlled immutable financial adjustments.

    Core rules:
        - NEVER mutate historical records
        - ALWAYS emit immutable financial events
        - ALL corrections remain auditable
    """

    @staticmethod
    @transaction.atomic
    def apply_adjustment(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        created_by: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FinancialEvent:
        """
        Create immutable adjustment financial event.

        Positive amount:
            Credit adjustment

        Negative amount:
            Deduction adjustment
        """

        if amount == Decimal("0.00"):
            raise ValueError(
                "Adjustment amount cannot be zero."
            )

        event_metadata: dict[str, Any] = {
            "reason": reason,
            "source": "adjustment_service",
            "generated_at": timezone.now().isoformat(),
        }

        if metadata:
            event_metadata.update(metadata)

        event = FinancialEvent.objects.create(
            website=website,
            writer=writer,
            event_type=FinancialEventType.ADJUSTMENT,
            status=FinancialEventStatus.MATURED,
            amount=amount,
            title="Financial Adjustment",
            description=reason,
            created_by=created_by,
            metadata=event_metadata,
        )

        # Durable event propagation
        OutboxService.emit(
            event_type="FINANCIAL_EVENT_CREATED",
            payload={
                "financial_event_id": str(event.pk),
                "event_type": FinancialEventType.ADJUSTMENT,
            },
        )

        return event
