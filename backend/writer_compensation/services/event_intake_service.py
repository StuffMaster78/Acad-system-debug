from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from writer_compensation.enums.compensation_enums import (
    EventStatus,
    EventType,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    InvalidPayoutItemTransitionError,
    InvalidWindowTransitionError,
    NoOpenWindowError,
    WindowLockedError,
    ZeroAmountError,
)

from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)


class EventIntakeService:
    """
    The single entry point for ALL earning and deduction events.

    No producer app should create a CompensationEvent directly.
    All creation goes through record().

    Enforces:
    - Non-zero amount
    - Open window exists for this website
    - Window is not locked
    - Idempotency (get_or_create when key is provided)
    """

    @staticmethod
    @transaction.atomic
    def record(
        *,
        website,
        writer,
        event_type: str,
        amount: Decimal,
        source: str = "",
        source_type: str = "",
        source_id: int | None = None,
        title: str = "",
        notes: str = "",
        idempotency_key: str = "",
        created_by=None,
        related_window: PaymentWindow | None = None,
    ) -> tuple[CompensationEvent, bool]:
        """
        Create a CompensationEvent and assign it to the current open window.

        Returns (event, created: bool).

        For post-close adjustments pass related_window=<closed_window>.
        The event is still assigned to the next open window.

        Raises:
            ZeroAmountError — amount is zero
            NoOpenWindowError — no OPEN window for this website
            WindowLockedError — open window is somehow locked (shouldn't happen)
        """
        if amount == Decimal("0.00"):
            raise ZeroAmountError("Compensation event amount cannot be zero.")

        open_window = (
            PaymentWindow.objects
            .filter(website=website, status=WindowStatus.OPEN)
            .order_by("-start_date")
            .first()
        )
        if open_window is None:
            raise NoOpenWindowError(
                f"No open compensation window for website {website.pk}."
            )

        if open_window.is_locked:
            raise WindowLockedError(
                f"Window {open_window.pk} is locked ({open_window.status})."
            )

        defaults = dict(
            payment_window=open_window,
            event_type=event_type,
            amount=amount,
            status=EventStatus.PENDING_CONFIRMATION,
            source=source,
            source_type=source_type,
            source_id=source_id,
            title=title or event_type,
            notes=notes,
            created_by=created_by,
            related_window=related_window,
        )

        if idempotency_key:
            event, created = CompensationEvent.objects.get_or_create(
                website=website,
                writer=writer,
                idempotency_key=idempotency_key,
                defaults=defaults,
            )
        else:
            # No idempotency key — always create, store blank string.
            event = CompensationEvent.objects.create(
                website=website,
                writer=writer,
                idempotency_key="",
                **defaults,
            )
            created = True

        return event, created

    @staticmethod
    @transaction.atomic
    def mature_event(event: CompensationEvent) -> CompensationEvent:
        """
        PENDING_CONFIRMATION → MATURED.

        A matured event is eligible for settlement aggregation.
        Called by admin review, or automatically when a window closes
        with auto_confirm_pending=True.
        """
        if event.status != EventStatus.PENDING_CONFIRMATION:
            raise InvalidWindowTransitionError(
                f"Event {event.pk} is {event.status}. "
                "Expected PENDING_CONFIRMATION."
            )
        event.status = EventStatus.MATURED
        event.matured_at = timezone.now()
        event.save(update_fields=["status", "matured_at"])
        return event

    @staticmethod
    @transaction.atomic
    def void_event(
        event: CompensationEvent,
        voided_by,
        reason: str = "",
    ) -> CompensationEvent:
        """
        Any non-PAID status → VOIDED.
        Admin use only. Cannot void a paid event.
        """
        if event.status == EventStatus.PAID:
            raise InvalidWindowTransitionError(
                f"Event {event.pk} is PAID and cannot be voided."
            )
        event.status = EventStatus.VOIDED
        if reason:
            event.notes = f"{event.notes}\n[VOIDED] {reason}".strip()
        event.save(update_fields=["status", "notes"])
        return event

    @staticmethod
    @transaction.atomic
    def create_reversal(
        original_event: CompensationEvent,
        created_by,
        notes: str = "",
    ) -> CompensationEvent:
        """
        Creates a REVERSAL event that negates the original event.
        The original event is stamped REVERSED.
        Both events must be on the same website/writer.
        """
        if original_event.status == EventStatus.REVERSED:
            raise InvalidWindowTransitionError(
                f"Event {original_event.pk} is already REVERSED."
            )

        reversal, _ = EventIntakeService.record(
            website=original_event.website,
            writer=original_event.writer,
            event_type=EventType.REVERSAL,
            amount=-original_event.amount,
            source_type=original_event.source_type,
            source_id=original_event.source_id,
            title=f"Reversal of event {original_event.pk}",
            notes=notes or f"Reversal of {original_event.event_type} #{original_event.pk}",
            created_by=created_by,
        )

        # Link and stamp original.
        # reversal.related_event = original_event
        # reversal.save(update_fields=["related_event"])
        CompensationEvent.objects.filter(pk=reversal.pk).update(
            related_event=original_event,
        )

        original_event.status = EventStatus.REVERSED
        original_event.reversed_at = timezone.now()
        original_event.save(update_fields=["status", "reversed_at"])

        return reversal

    @staticmethod
    @transaction.atomic
    def confirm_event(event: CompensationEvent) -> CompensationEvent:
        """
        Move a single event from PENDING to CONFIRMED.
        Called by admin or automatically when window closes.
        """
        if event.status != EventStatus.PENDING_CONFIRMATION:
            raise InvalidPayoutItemTransitionError(
                f"Event {event.pk} is {event.status}, not PENDING."
            )
        event.status = EventStatus.MATURED
        event.save(update_fields=["status"])
        return event