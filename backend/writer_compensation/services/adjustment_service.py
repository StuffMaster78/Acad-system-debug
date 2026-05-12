from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_compensation.enums.financial_event_enums import (
    FinancialEventStatus,
    FinancialEventType,
)

from writer_compensation.models.compensation_event import (
    CompensationEvent,
)

from writer_compensation.services.outbox_service import (
    OutboxService,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.services.event_intake_service import (
    EventIntakeService,
)
from writer_compensation.enums.compensation_enums import (
    WindowStatus,
    EventType,
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
    ) -> CompensationEvent:
        """
        Create immutable adjustment  compensation event.

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

        event = CompensationEvent.objects.create(
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
    

    @staticmethod
    @transaction.atomic
    def create_post_close_adjustment(
        *,
        closed_window: PaymentWindow,
        writer,
        amount: Decimal,
        notes: str,
        created_by,
    ) -> CompensationEvent:
        """
        Creates an ADJUSTMENT event in the current open window that references
        the closed window. Amount can be positive (missed earning) or negative
        (over-payment correction).
 
        Raises:
            ValueError — closed_window is not PROCESSING or DONE
            ZeroAmountError — amount is zero
            NoOpenWindowError — no open window exists
        """
        if closed_window.status not in {
            WindowStatus.PROCESSING,
            WindowStatus.DONE,
        }:
            raise ValueError(
                "Post-close adjustments only apply to PROCESSING or DONE windows. "
                f"Window {closed_window.pk} is {closed_window.status}."
            )
 
        event, _ = EventIntakeService.record(
            website=closed_window.website,
            writer=writer,
            event_type=EventType.ADJUSTMENT,
            amount=amount,
            notes=notes,
            created_by=created_by,
            related_window=closed_window,
        )
        return event
