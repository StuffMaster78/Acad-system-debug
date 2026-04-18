from __future__ import annotations

from django.db import models


class UnpaidOrderDispatchStatus(models.TextChoices):
    """
    Dispatch execution state for scheduled unpaid order reminders.
    """

    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    SKIPPED = "skipped", "Skipped"