from __future__ import annotations
 
from decimal import Decimal
 
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
 
from writer_compensation.enums.compensation_enums import (
    EventStatus,
    PayoutRecordStatus,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    InvalidWindowTransitionError,
    WindowOverlapError,

)
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.payout_batch import (
    PayoutBatch,
)
from writer_compensation.models.payout_record import (
    PayoutRecord,
)


class WindowService:
    """
    All CompensationWindow lifecycle transitions.
    No transition logic lives anywhere else.
    """
 
    @staticmethod
    @transaction.atomic
    def create_window(
        *,
        website,
        cycle_type: str,
        start_date,
        end_date,
        title: str = "",
        created_by=None,
    ) -> PaymentWindow:
        """
        Create a new compensation window.
 
        Validates:
        - start_date < end_date
        - No overlap with existing UPCOMING, OPEN, or CLOSED windows for this site
        """
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date.")
 
        overlap = PaymentWindow.objects.filter(
            website=website,
            status__in=[
                WindowStatus.UPCOMING,
                WindowStatus.OPEN,
                WindowStatus.CLOSED,
            ],
        ).filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        ).exists()
 
        if overlap:
            raise WindowOverlapError(
                "A window already exists covering this date range."
            )
        
        generated_title = (
            title
            or f"{cycle_type.title()} {start_date} - {end_date}"
        )
 
        return PaymentWindow.objects.create(
            website=website,
            cycle_type=cycle_type,
            title=generated_title,
            start_date=start_date,
            end_date=end_date,
            status=WindowStatus.OPEN,
            created_by=created_by,
        )
 
    @staticmethod
    @transaction.atomic
    def close_window(
        window: PaymentWindow,
        closed_by,
        auto_confirm_pending: bool = False,
    ) -> PaymentWindow:
        """
        OPEN → CLOSED.
 
        - Confirms all PENDING events if auto_confirm_pending=True.
        - Aggregates CONFIRMED events per writer.
        - Creates PayoutBatch and one PayoutItem per writer.
        - Does NOT auto-create the next window — caller decides.
 
        Raises InvalidWindowTransitionError if window is not OPEN.
        """
        if window.status != WindowStatus.OPEN:
            raise InvalidWindowTransitionError(
                f"Window {window.pk} is {window.status}. Expected OPEN."
            )
 
        # Optionally confirm all pending events before closing.
        if auto_confirm_pending:
            CompensationEvent.objects.filter(
                window=window,
                status=EventStatus.PENDING_CONFIRMATION,
            ).update(status=EventStatus.MATURED)
 
        # Transition window.
        window.status    = WindowStatus.CLOSED
        window.closed_at = timezone.now()
        window.save(update_fields=["status", "closed_at", "updated_at"])
 
        # Aggregate MATURED events per writer.
        writer_totals = (
            CompensationEvent.objects
            .filter(window=window, status=EventStatus.MATURED)
            .values("writer_id")
            .annotate(total=Sum("amount"))
        )
 
        # Create the batch — OneToOne so this will IntegrityError
        # if called twice on the same window (correct behaviour).
        batch = PayoutBatch.objects.create(
            website=window.website,
            payment_window=window,
            title=f"Batch — {window.title}",
            created_by=closed_by,
        )
 
        # Bulk-create one PayoutRecord per writer.
        # NOTE: settlement_period intentionally omitted — it is nullable
        # and will be linked later by the settlement pipeline.
        records = [
            PayoutRecord(
                website=window.website,
                batch=batch,
                writer_id=row["writer_id"],
                total_amount=row["total"] or Decimal("0.00"),
                status=PayoutRecordStatus.PENDING,
            )
            for row in writer_totals
        ]
        PayoutRecord.objects.bulk_create(records)
 
        # Denormalise batch total (positive items only — informational).
        batch.total_amount = sum(
            (r.total_amount for r in records if r.total_amount > Decimal("0.00")),
            Decimal("0.00"),
        )
        batch.total_writers = len(records)
        batch.save(update_fields=["total_amount", "total_writers", "updated_at"])
 
        return window
 
    @staticmethod
    @transaction.atomic
    def start_processing(window: PaymentWindow) -> PaymentWindow:
        """
        CLOSED → PROCESSING.
 
        - Writers now see "Payment being processed" on their dashboard.
        - All events in this window become immutable.
 
        Raises InvalidWindowTransitionError if window is not CLOSED.
        """
        if window.status != WindowStatus.CLOSED:
            raise InvalidWindowTransitionError(
                f"Window {window.pk} is {window.status}. Expected CLOSED."
            )
 
        window.status = WindowStatus.PROCESSING
        window.processing_at = timezone.now()
        window.save(update_fields=["status", "processing_at", "updated_at"])
 
        # Lock all events — confirm any still-pending ones.
        CompensationEvent.objects.filter(
            window=window,
            status=EventStatus.PENDING_CONFIRMATION,
        ).update(status=EventStatus.MATURED)
 
        # Fire signal for writer notifications (handled in signals.py).
        from writer_compensation.signals import window_processing_started
        window_processing_started.send(
            sender=PaymentWindow,
            window=window,
        )
 
        return window
 
    @staticmethod
    @transaction.atomic
    def mark_done(window: PaymentWindow) -> PaymentWindow:
        """
        PROCESSING → DONE.
 
        Held PayoutItems remain HELD indefinitely — window closure does not
        affect them. Admin resolves them separately.
 
        Raises InvalidWindowTransitionError if window is not PROCESSING.
        """
        if window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                f"Window {window.pk} is {window.status}. Expected PROCESSING."
            )
 
        window.status  = WindowStatus.DONE
        window.done_at = timezone.now()
        window.save(update_fields=["status", "done_at", "updated_at"])
 
        return window
 
    @staticmethod
    def get_or_create_next_window(
        website,
        cycle_type: str,
        after_window: PaymentWindow,
        created_by=None,
    ) -> tuple[PaymentWindow, bool]:
        """
        Convenience: create the next window immediately after after_window.
        Returns (window, created).
        Useful to call after close_window() to ensure there is always an open window.
        """
        from datetime import timedelta
        next_start = after_window.end_date + timedelta(days=1)
 
        if cycle_type == "biweekly":
            next_end = next_start + timedelta(days=13)  # 14-day window
        else:
            # Monthly: end on last day of the following month.
            import calendar
            year  = next_start.year + (next_start.month // 12)
            month = (next_start.month % 12) + 1
            last  = calendar.monthrange(year, month)[1]
            from datetime import date
            next_end = date(year, month, last)
 
        try:
            window = WindowService.create_window(
                website=website,
                cycle_type=cycle_type,
                start_date=next_start,
                end_date=next_end,
                created_by=created_by,
            )
            return window, True
        except WindowOverlapError:
            window = PaymentWindow.objects.get(
                website=website,
                start_date=next_start,
                cycle_type=cycle_type,
            )
            return window, False