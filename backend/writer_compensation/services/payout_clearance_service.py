from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from websites.models.websites import Website

User = settings.AUTH_USER_MODEL


class ClearanceStatus(models.TextChoices):
    PENDING    = "PENDING",    "Pending"
    PROCESSING = "PROCESSING", "Processing"
    PAID       = "PAID",       "Paid"
    FAILED     = "FAILED",     "Failed"


class PayoutClearance(models.Model):
    """
    Real-world payout execution record.

    Confirms money actually left the platform via
    MPESA, bank transfer, PayPal, Wise, etc.

    This is NOT the payment intent — PayoutRecord is the intent.
    This is the external proof that the payment happened.

    Immutable once status = PAID.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.PROTECT,          # FIX: was CASCADE
        related_name="payout_clearances",
    )
    payout_record = models.ForeignKey(
        "writer_compensation.PayoutRecord", # FIX: was writer_payments_management
        on_delete=models.PROTECT,          # FIX: was CASCADE — proof must outlive intent
        related_name="clearances",
    )

    # FIX: renamed from amount_sent → amount_paid (matches service)
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    method = models.CharField(
        max_length=64,
        blank=True,
        help_text="MPESA, Bank, PayPal, Wise, etc.",
    )

    # FIX: renamed from external_reference → external_transaction_id (matches service)
    external_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Transaction ID from the external payment provider.",
    )

    # FIX: uses TextChoices enum — was raw string default
    status = models.CharField(
        max_length=32,
        choices=ClearanceStatus.choices,
        default=ClearanceStatus.PENDING,
        db_index=True,
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payout_clearances",
    )
    processed_at   = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    metadata       = models.JSONField(default=dict, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["payout_record", "status"]),
            models.Index(fields=["external_transaction_id"]),
            models.Index(fields=["website", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"Clearance {self.pk} | "
            f"record {self.payout_record.pk} | "
            f"{self.amount_paid} | "
            f"{self.status}"
        )