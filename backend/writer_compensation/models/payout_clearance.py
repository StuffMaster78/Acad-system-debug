from __future__ import annotations

from django.conf import settings
from django.db import models

from websites.models.websites import Website


User = settings.AUTH_USER_MODEL


class PayoutClearance(models.Model):
    """
    Real world payout execution record.

    This confirms:
        money actually left the platform
        via MPESA, bank, PayPal, etc
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="payout_clearances",
    )

    payout_record = models.ForeignKey(
        "writer_compensation.PayoutRecord",
        on_delete=models.CASCADE,
        related_name="clearances",
    )

    amount_sent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    method = models.CharField(
        max_length=64,
        help_text="MPESA, Bank, PayPal, Wise, etc",
    )

    external_reference = models.CharField(
        max_length=255,
        blank=True,
    )

    status = models.CharField(
        max_length=32,
        default="PENDING",
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payout_clearances",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payout_record.pk} | {self.amount_sent} | {self.status}"
