"""
Management command: backfill_compensation_events

Creates CompensationEvent rows for completed orders that were processed
before Celery was wired (so no event was fired at completion time).

Safe to re-run: idempotency_key prevents duplicate rows.

Usage:
    python manage.py backfill_compensation_events
    python manage.py backfill_compensation_events --dry-run
    python manage.py backfill_compensation_events --website-id=3
    python manage.py backfill_compensation_events --status=matured   # default
    python manage.py backfill_compensation_events --status=pending
"""
from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Backfill CompensationEvent rows for completed orders missing an earnings event."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
        parser.add_argument("--website-id", type=int, default=None, help="Limit to one website.")
        parser.add_argument(
            "--status",
            choices=["matured", "pending"],
            default="matured",
            help="Status to assign to backfilled events (default: matured).",
        )

    def handle(self, *args, **options):
        from orders.models.orders import Order
        from orders.models.orders.order_assignment import OrderAssignment
        from writer_compensation.enums.compensation_enums import EventSource, EventStatus, EventType
        from writer_compensation.models.compensation_event import CompensationEvent
        from writer_compensation.models.payment_window import PaymentWindow

        dry_run = options["dry_run"]
        website_id = options["website_id"]
        target_status = (
            EventStatus.MATURED if options["status"] == "matured"
            else EventStatus.PENDING_CONFIRMATION
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no rows will be written."))

        # All completed orders that already have an event for that source_id
        existing_source_ids = set(
            CompensationEvent.objects.filter(
                source_type="order",
                event_type=EventType.ORDER_EARNING,
            ).values_list("source_id", flat=True)
        )

        qs = (
            Order.objects.filter(status="completed")
            .select_related("website")
            .exclude(pk__in=existing_source_ids)
        )
        if website_id:
            qs = qs.filter(website_id=website_id)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nothing to backfill."))
            return

        self.stdout.write(f"Found {total} orders to backfill.")

        created_count = 0
        skipped_count = 0

        for order in qs.iterator(chunk_size=200):
            # Must have a writer assignment
            assignment = (
                OrderAssignment.objects.filter(order=order, is_current=True)
                .select_related("writer")
                .first()
            )
            if assignment is None:
                self.stdout.write(
                    self.style.WARNING(f"  Order {order.pk}: no current writer assignment — skip.")
                )
                skipped_count += 1
                continue

            writer = assignment.writer

            # Must have a non-zero compensation figure
            amount = order.writer_compensation or Decimal("0.00")
            if amount <= 0:
                self.stdout.write(
                    self.style.WARNING(f"  Order {order.pk}: writer_compensation=0 — skip.")
                )
                skipped_count += 1
                continue

            # Find the best payment window for this order
            window = self._best_window(PaymentWindow, order)
            if window is None:
                self.stdout.write(
                    self.style.WARNING(f"  Order {order.pk}: no payment window for website {order.website_id} — skip.")
                )
                skipped_count += 1
                continue

            idempotency_key = f"backfill_order_{order.pk}"

            if dry_run:
                self.stdout.write(
                    f"  [dry-run] Order {order.pk}: writer={writer.pk}, "
                    f"amount={amount}, window={window.pk}"
                )
                created_count += 1
                continue

            with transaction.atomic():
                event, created = CompensationEvent.objects.get_or_create(
                    website=order.website,
                    writer=writer,
                    idempotency_key=idempotency_key,
                    defaults={
                        "payment_window": window,
                        "event_type": EventType.ORDER_EARNING,
                        "source": EventSource.ORDER,
                        "source_type": "order",
                        "source_id": order.pk,
                        "amount": amount,
                        "currency": getattr(order, "currency", "USD") or "USD",
                        "title": f"Order #{order.pk}",
                        "description": order.topic or "",
                        "reference": str(order.pk),
                        "status": target_status,
                        "is_visible_to_writer": True,
                        "notes": "Backfilled by backfill_compensation_events command.",
                        "matured_at": timezone.now() if target_status == EventStatus.MATURED else None,
                    },
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1  # already existed (race or re-run)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}  Skipped: {skipped_count}"
                + (" (dry run)" if dry_run else "")
            )
        )

    @staticmethod
    def _best_window(PaymentWindow, order):
        """
        Return the most appropriate payment window for this order.

        Priority:
        1. Window whose date range contains the order completion date
        2. Most recent window that ended before the completion date
        3. Any window for the website (most recent by start_date)
        """
        completed = getattr(order, "completed_at", None) or getattr(order, "created_at", None)
        if completed is not None:
            completion_date = completed.date() if hasattr(completed, "date") else completed

            # Exact period match
            window = (
                PaymentWindow.objects.filter(
                    website=order.website,
                    start_date__lte=completion_date,
                    end_date__gte=completion_date,
                )
                .order_by("-start_date")
                .first()
            )
            if window:
                return window

            # Most recent window that closed before the completion
            window = (
                PaymentWindow.objects.filter(
                    website=order.website,
                    end_date__lt=completion_date,
                )
                .order_by("-end_date")
                .first()
            )
            if window:
                return window

        # Any window for the website
        return (
            PaymentWindow.objects.filter(website=order.website)
            .order_by("-start_date")
            .first()
        )
