from __future__ import annotations

import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone

from pricing_configs.models import AdditionalService
from orders.models import Order, DraftRequest, DraftFile


class Command(BaseCommand):
    """Backfill draft requests for orders that purchased Progressive Delivery."""

    help = "Backfill draft requests for orders that purchased Progressive Delivery."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of orders to backfill (default: all eligible).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only report what would happen without writing to the database.",
        )
        parser.add_argument(
            "--per-order",
            type=int,
            default=1,
            help="Number of draft requests to create per eligible order (default: 1).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        per_order = max(1, options["per_order"])
        limit = options.get("limit")

        progressive_services = AdditionalService.objects.filter(is_active=True).filter(
            models.Q(slug__iexact="progressive-delivery")
            | models.Q(service_name__icontains="progressive")
            | models.Q(service_name__icontains="draft")
        )

        if not progressive_services.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No progressive delivery services found. Nothing to backfill."
                )
            )
            return

        eligible_orders = (
            Order.objects.filter(
                is_paid=True,
                client__isnull=False,
                extra_services__in=progressive_services,
            )
            .filter(draft_requests__isnull=True)
            .select_related("website", "client", "assigned_writer")
            .distinct()
            .order_by("-created_at")
        )

        if limit:
            eligible_orders = eligible_orders[:limit]

        total_orders = eligible_orders.count()
        if not total_orders:
            self.stdout.write(
                self.style.WARNING(
                    "No eligible orders found for draft request backfill."
                )
            )
            return

        self.stdout.write(
            f"Found {total_orders} eligible orders. Creating up to {per_order} draft request(s) per order."
        )

        created_requests = 0
        created_files = 0

        for order in eligible_orders:
            for _ in range(per_order):
                status = self._infer_status(order)
                requested_at = self._random_requested_at(order)

                if dry_run:
                    created_requests += 1
                    if status == "fulfilled":
                        created_files += 1
                    continue

                with transaction.atomic():
                    draft_request = DraftRequest.objects.create(
                        website=order.website,
                        order=order,
                        requested_by=order.client,
                        status=status,
                        message=self._random_message(status),
                    )

                    DraftRequest.objects.filter(pk=draft_request.pk).update(
                        requested_at=requested_at
                    )
                    draft_request.refresh_from_db()

                    if status == "fulfilled":
                        draft_request.fulfilled_at = (
                            draft_request.requested_at
                            + timedelta(hours=random.randint(6, 36))
                        )
                        draft_request.save(update_fields=["fulfilled_at"])
                        draft_file = self._create_draft_file(draft_request)
                        if draft_file:
                            created_files += 1

                created_requests += 1

        summary = (
            f"{'Dry run:' if dry_run else 'Done:'} "
            f"{created_requests} draft request(s) "
            f"{'(simulated)' if dry_run else ''}"
        )
        if created_files:
            summary += f", {created_files} draft file(s)"
        self.stdout.write(self.style.SUCCESS(summary))

    def _infer_status(self, order: Order) -> str:
        """Pick a sensible status based on order state."""
        if order.status in {"completed", "approved", "delivered"}:
            return "fulfilled"
        if order.status in {"in_progress", "revision", "on_hold"}:
            return random.choice(["pending", "in_progress"])
        return "pending"

    def _random_requested_at(self, order: Order):
        """Generate a requested_at timestamp anchored to order timeline."""
        base = order.created_at or timezone.now()
        offset_days = random.randint(0, 10)
        requested_at = base + timedelta(days=offset_days)
        return min(requested_at, timezone.now())

    def _random_message(self, status: str) -> str:
        """Provide a simple message for variety."""
        templates = {
            "pending": [
                "Could I see the first half of the draft?",
                "Please share the current progress for review.",
                "I'd like to verify the outline and intro.",
            ],
            "in_progress": [
                "Client requested more citations; updating draft.",
                "Working on the methodology section now.",
            ],
            "fulfilled": [
                "Draft ready for the client's review.",
                "Uploaded the completed first draft with references.",
            ],
        }
        pool = templates.get(status, templates["pending"])
        return random.choice(pool)

    def _create_draft_file(self, draft_request: DraftRequest) -> DraftFile | None:
        """Create a lightweight text file to simulate a draft upload."""
        order = draft_request.order
        uploaded_by = order.assigned_writer

        content = (
            f"Draft for order #{order.id}\n"
            f"Topic: {order.topic}\n"
            f"Generated on {timezone.now():%Y-%m-%d %H:%M}\n"
        ).encode("utf-8")

        filename = f"draft-order-{order.id}-{draft_request.id}.txt"
        file_obj = ContentFile(content, name=filename)

        return DraftFile.objects.create(
            website=order.website,
            draft_request=draft_request,
            order=order,
            uploaded_by=uploaded_by,
            file=file_obj,
            file_name=filename,
            description="Auto-generated draft for historical backfill",
        )

