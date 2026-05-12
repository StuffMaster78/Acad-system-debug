# models/deferred_settlement_models.py

from __future__ import annotations

from django.conf import settings
from django.db import models

from writer_compensation.enums.compensation_enums import (
    DeferralReason,
)
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)


User = settings.AUTH_USER_MODEL


class DeferredSettlementItem(models.Model):
    """
    Tracks settlement items moved
    from one compensation window to another.
    """

    financial_event = models.ForeignKey(
        CompensationEvent,
        on_delete=models.CASCADE,
        related_name="deferrals",
    )

    from_payment_window = models.ForeignKey(
        PaymentWindow,
        on_delete=models.CASCADE,
        related_name="outgoing_deferrals",
    )

    to_payment_window = models.ForeignKey(
        PaymentWindow,
        on_delete=models.CASCADE,
        related_name="incoming_deferrals",
    )

    reason = models.CharField(
        max_length=64,
        choices=DeferralReason.choices,
    )

    notes = models.TextField(
        blank=True,
    )

    deferred_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_payment_deferrals",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self) -> str:
        return (
            f"{self.financial_event.pk} | "
            f"{self.reason}"
        )
