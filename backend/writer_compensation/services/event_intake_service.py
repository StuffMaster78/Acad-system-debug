from __future__ import annotations
 
from decimal import Decimal
 
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
 
from writer_compensation.enums.compensation_enums import (
    EventStatus,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    InvalidPayoutItemTransitionError,
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
 
 
# ---------------------------------------------------------------------------
# EventIntakeService
# ---------------------------------------------------------------------------
 
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
        source_type: str = "",
        source_id: int | None = None,
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
            ZeroAmountError          — amount is zero
            NoOpenWindowError        — no OPEN window for this website
            WindowLockedError        — open window is somehow locked (shouldn't happen)
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
            window=open_window,
            event_type=event_type,
            amount=amount,
            status=EventStatus.PENDING,
            source_type=source_type,
            source_id=source_id,
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
    def confirm_event(event: CompensationEvent) -> CompensationEvent:
        """
        Move a single event from PENDING to CONFIRMED.
        Called by admin or automatically when window closes.
        """
        if event.status != EventStatus.PENDING:
            raise InvalidPayoutItemTransitionError(
                f"Event {event.pk} is {event.status}, not PENDING."
            )
        event.status = EventStatus.CONFIRMED
        event.save(update_fields=["status"])
        return event