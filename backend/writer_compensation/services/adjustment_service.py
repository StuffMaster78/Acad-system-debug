from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_compensation.enums.compensation_enums import ( # unified enum only
    EventStatus,
    EventType,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import ZeroAmountError
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.services.event_intake_service import EventIntakeService
from writer_compensation.services.outbox_service import OutboxService
from writer_compensation.signals import adjustment_event_created


class AdjustmentService:
    """
    Handles controlled immutable financial adjustments.

    Core rules:
        - NEVER mutate historical records
        - ALWAYS emit events via EventIntakeService (never direct DB create)
        - ALL corrections remain auditable
        - Positive amount = credit (writer receives more)
        - Negative amount = deduction (writer receives less)
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
        adjustment: Any | None = None,
    ) -> Any:
        """
        Create an immutable ADJUSTMENT CompensationEvent.

        FIX: previously called CompensationEvent.objects.create() directly,
        producing orphan events with no payment_window, no idempotency,
        and no window lock check. Now routes through EventIntakeService.record().

        The event is immediately matured (status = MATURED) because admin
        adjustments are confirmed at creation time — they do not need a
        separate review step.

        Pass `adjustment` (a CompensationAdjustment instance) when the call
        originates from an admin correction record — it will be stamped
        is_applied=True and linked to the created event.

        Raises:
            ZeroAmountError — amount is zero
            NoOpenWindowError — no open window exists for this website
        """
        if amount == Decimal("0.00"):
            raise ZeroAmountError("Adjustment amount cannot be zero.")

        event_metadata: dict[str, Any] = {
            "reason": reason,
            "source": "adjustment_service",
            "generated_at": timezone.now().isoformat(),
        }
        if metadata:
            event_metadata.update(metadata)

        # FIX: route through EventIntakeService — assigns window, checks
        # lock, enforces idempotency, fires with correct status.
        event, _ = EventIntakeService.record(
            website=website,
            writer=writer,
            event_type=EventType.ADJUSTMENT,
            amount=amount,
            title="Financial adjustment",
            notes=reason,
            created_by=created_by,
        )

        # Mature immediately — admin adjustments are pre-approved.
        event.status = EventStatus.MATURED
        event.metadata = event_metadata
        event.save(update_fields=["status", "metadata"])

        OutboxService.emit(
            event_type="FINANCIAL_EVENT_CREATED",
            payload={
                "financial_event_id": str(event.pk),
                "event_type": EventType.ADJUSTMENT,
                "amount": str(amount),
            },
        )

        # Mark the admin adjustment record applied if one was supplied.
        if adjustment is not None:
            adjustment.is_applied = True
            adjustment.applied_at = timezone.now()
            adjustment.related_financial_event = event
            adjustment.save(update_fields=["is_applied", "applied_at", "related_financial_event"])

        # Notify the writer (handler: on_adjustment_event_created).
        adjustment_event_created.send(sender=AdjustmentService, event=event)

        return event

    @staticmethod
    @transaction.atomic
    def create_post_close_adjustment(
        *,
        closed_window: PaymentWindow,
        writer: Any,
        amount: Decimal,
        notes: str,
        created_by: Any,
    ) -> Any:
        """
        Creates an ADJUSTMENT event in the current open window that
        references the closed window being corrected.

        Amount can be positive (missed earning) or negative
        (over-payment correction).

        Raises:
            ValueError — closed_window is not PROCESSING or DONE
            ZeroAmountError — amount is zero
            NoOpenWindowError — no open window exists
        """
        if amount == Decimal("0.00"):
            raise ZeroAmountError("Adjustment amount cannot be zero.")

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