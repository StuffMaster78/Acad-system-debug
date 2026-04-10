from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ledger.constants import HoldStatus


class HoldRecord(models.Model):
    """
    Represents a reservation of funds before final capture or release.

    Example use cases:
        wallet funds reserved during split checkout
        dispute related hold
        temporary reservation before external gateway confirmation
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="ledger_holds",
    )
    ledger_account = models.ForeignKey(
        "ledger.LedgerAccount",
        on_delete=models.PROTECT,
        related_name="hold_records",
    )
    journal_entry = models.ForeignKey(
        "ledger.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hold_records",
        help_text="Optional originating journal entry for this hold.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_holds",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    status = models.CharField(
        max_length=20,
        choices=HoldStatus.choices,
        default=HoldStatus.ACTIVE,
    )
    reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Business reference, e.g. order ref or payment ref.",
    )
    reason = models.TextField(
        blank=True,
        default="",
    )
    wallet_reference = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    payment_intent_reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )
    related_object_type = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Related business model, e.g. Order, Dispute.",
    )
    related_object_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    captured_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    released_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "ledger_hold_records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "ledger_account"]),
            models.Index(fields=["website", "user"]),
            models.Index(fields=["website", "wallet_reference"]),
            models.Index(fields=["website", "payment_intent_reference"]),
            models.Index(fields=["website", "reference"]),
            models.Index(fields=["website", "related_object_type", "related_object_id"]),
            models.Index(fields=["website", "expires_at"]),
        ]
        verbose_name = "Hold Record"
        verbose_name_plural = "Hold Records"

    def __str__(self) -> str:
        return f"{self.reference or self.id} | {self.status} | {self.amount}"

    @property
    def is_active(self) -> bool:
        return self.status == HoldStatus.ACTIVE

    @property
    def is_captured(self) -> bool:
        return self.status == HoldStatus.CAPTURED

    @property
    def is_released(self) -> bool:
        return self.status == HoldStatus.RELEASED

    @property
    def is_expired(self) -> bool:
        return self.status == HoldStatus.EXPIRED

    @property
    def is_cancelled(self) -> bool:
        return self.status == HoldStatus.CANCELLED

    @property
    def is_final(self) -> bool:
        return self.status in {
            HoldStatus.CAPTURED,
            HoldStatus.RELEASED,
            HoldStatus.EXPIRED,
            HoldStatus.CANCELLED,
        }

    def mark_captured(self) -> None:
        self.status = HoldStatus.CAPTURED
        self.captured_at = timezone.now()

    def mark_released(self) -> None:
        self.status = HoldStatus.RELEASED
        self.released_at = timezone.now()

    def mark_cancelled(self) -> None:
        self.status = HoldStatus.CANCELLED
        self.cancelled_at = timezone.now()

    def mark_expired(self) -> None:
        self.status = HoldStatus.EXPIRED

    def clean(self) -> None:
        if self.amount is None:
            raise ValidationError({"amount": "Amount is required."})

        if self.amount <= Decimal("0.00"):
            raise ValidationError(
                {"amount": "Amount must be greater than zero."}
            )

        comparison_time = self.created_at or timezone.now()

        if self.expires_at and self.expires_at <= comparison_time:
            raise ValidationError(
                {"expires_at": "Expiry time must be later than creation time."}
            )