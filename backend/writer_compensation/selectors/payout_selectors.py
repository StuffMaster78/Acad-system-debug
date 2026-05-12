from __future__ import annotations
 
from django.db.models import Count
 
from writer_compensation.enums.compensation_enums import (
    PayoutItemStatus,
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


class PayoutSelectors:
 
    @staticmethod
    def get_batch_for_window(window: PaymentWindow) -> PayoutBatch | None:
        try:
            return (
                PayoutBatch.objects
                .prefetch_related("items__writer")
                .get(window=window)
            )
        except PayoutBatch.DoesNotExist:
            return None
 
    @staticmethod
    def get_record_for_writer(batch: PayoutBatch, writer) -> PayoutRecord | None:
        return PayoutRecord.objects.filter(batch=batch, writer=writer).first()
 
    @staticmethod
    def get_pending_records(batch: PayoutBatch):
        return batch.records.filter(status=PayoutItemStatus.PENDING)
 
    @staticmethod
    def get_held_items_for_site(website):
        """All held payout items site-wide — admin / support priority queue."""
        return (
            PayoutRecord.objects
            .filter(
                batch__window__website=website,
                status=PayoutItemStatus.HELD,
            )
            .select_related("writer", "batch__window")
            .order_by("-batch__created_at")
        )
 
    @staticmethod
    def get_writer_payout_history(writer):
        """All payout items for one writer across all windows."""
        return (
            PayoutRecord.objects
            .filter(writer=writer)
            .select_related("batch__window")
            .order_by("-batch__window__start_date")
        )
 
    @staticmethod
    def get_batch_record_counts(batch: PayoutBatch) -> dict:
        qs = batch.records.values("status").annotate(count=Count("id"))
        result = {row["status"]: row["count"] for row in qs}
        return {
            "pending":   result.get(PayoutItemStatus.PENDING,   0),
            "confirmed": result.get(PayoutItemStatus.CONFIRMED, 0),
            "paid":      result.get(PayoutItemStatus.PAID,      0),
            "held":      result.get(PayoutItemStatus.HELD,      0),
        }
 