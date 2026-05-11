from __future__ import annotations

from django.db.models import TextChoices


class TipStatus(TextChoices):
    """
    Lifecycle states for a tip transaction.
    """

    PENDING = "pending", "Pending"
    PAYMENT_INITIATED = "payment_initiated", "Payment Initiated"
    PROCESSING = "processing", "Processing"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"