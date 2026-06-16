"""
Seed writer payout records with sample data for the payment management view.

Creates PaymentWindow → PayoutBatch → PayoutRecord entries per website.
Safe to re-run — skips websites that already have payout records.
"""
from decimal import Decimal
from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from websites.models.websites import Website
from writer_management.models import WriterProfile
from writer_compensation.models import WriterPayment, PayoutBatch, PaymentWindow
from writer_compensation.enums.compensation_enums import (
    PayoutBatchStatus,
    PayoutRecordStatus,
    WindowStatus,
    WindowType,
)


class Command(BaseCommand):
    help = "Seed demo payout records (PaymentWindow → PayoutBatch → PayoutRecord) per website."

    def add_arguments(self, parser):
        parser.add_argument("--website-id", type=int, help="Seed only this website ID")
        parser.add_argument("--clear", action="store_true", help="Delete existing payout records first")
        parser.add_argument("--count", type=int, default=10, help="Writers to include per window (default: 10)")

    def handle(self, *args, **options):
        website_id = options.get("website_id")
        clear = options.get("clear", False)
        count = options.get("count", 10)

        websites = (
            Website.objects.filter(id=website_id) if website_id
            else Website.objects.filter(is_active=True)
        )
        if not websites.exists():
            self.stdout.write(self.style.WARNING("No active websites found."))
            return

        total_created = 0

        for website in websites:
            profiles = list(
                WriterProfile.objects.filter(
                    account_profile__website=website,
                    account_profile__user__is_active=True,
                )[:count]
            )
            if not profiles:
                self.stdout.write(f"  {website.name}: no writers — skipping")
                continue

            if clear:
                WriterPayment.objects.filter(website=website).delete()
                PayoutBatch.objects.filter(website=website).delete()
                PaymentWindow.objects.filter(website=website).delete()
                self.stdout.write(f"  {website.name}: cleared existing records")

            # Skip if already seeded
            if WriterPayment.objects.filter(website=website).exists():
                self.stdout.write(f"  {website.name}: already has payout records — skipping (use --clear to reseed)")
                continue

            today = date.today()

            # Create two windows: one completed, one open
            windows = [
                {
                    "title": f"{website.name} — Bi-weekly (Demo, Completed)",
                    "cycle_type": WindowType.BIWEEKLY,
                    "status": WindowStatus.DONE,
                    "start_date": today - timedelta(days=28),
                    "end_date": today - timedelta(days=15),
                    "payout_date": today - timedelta(days=14),
                    "record_status": PayoutRecordStatus.PAID,
                    "batch_status": PayoutBatchStatus.CLEARED,
                },
                {
                    "title": f"{website.name} — Bi-weekly (Demo, Open)",
                    "cycle_type": WindowType.BIWEEKLY,
                    "status": WindowStatus.OPEN,
                    "start_date": today - timedelta(days=14),
                    "end_date": today,
                    "payout_date": today + timedelta(days=1),
                    "record_status": PayoutRecordStatus.PENDING,
                    "batch_status": PayoutBatchStatus.DRAFT,
                },
            ]

            for wdata in windows:
                record_status = wdata.pop("record_status")
                batch_status = wdata.pop("batch_status")

                window = PaymentWindow.objects.create(website=website, **wdata)
                batch = PayoutBatch.objects.create(
                    website=website,
                    payment_window=window,
                    status=batch_status,
                    total_amount=Decimal("0.00"),
                )

                batch_total = Decimal("0.00")
                for profile in profiles:
                    amount = Decimal(str(random.uniform(80, 500))).quantize(Decimal("0.01"))
                    rec = WriterPayment.objects.create(
                        website=website,
                        batch=batch,
                        writer=profile,
                        total_amount=amount,
                        status=record_status,
                        notes="Demo record — seeded by seed_payment_management",
                        paid_at=timezone.now() if record_status == PayoutRecordStatus.PAID else None,
                    )
                    batch_total += amount
                    total_created += 1
                    self.stdout.write(f"  {rec.status} ${amount} — {profile.pen_name or profile.pk}")

                batch.total_amount = batch_total
                batch.save(update_fields=["total_amount"])

            self.stdout.write(self.style.SUCCESS(f"  {website.name}: done"))

        self.stdout.write(self.style.SUCCESS(f"\nDone. Created {total_created} payout records."))
