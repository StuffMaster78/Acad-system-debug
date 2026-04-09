from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ledger.constants import ReconciliationStatus


class ReconciliationRecord(models.Model):
    """
    Tracks reconciliation between internal ledger activity and external or
    operational payment records.

    Example use cases:
        gateway callback matched to payment intent and journal entry
        payout transaction matched to ledger posting
        refund confirmation matched to reversal entry
        mismatch investigation for admin review
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="ledger_reconciliations",
    )
    journal_entry = models.ForeignKey(
        "ledger.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciliation_records",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_reconciliations",
    )
    status = models.CharField(
        max_length=30,
        choices=ReconciliationStatus.choices,
        default=ReconciliationStatus.UNRECONCILED,
    )
    currency = models.CharField(
        max_length=10,
        default="KES",
    )
    expected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    actual_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    matched_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    variance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Internal business reference, e.g. payment or refund ref.",
    )
    external_reference = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Gateway or provider reference.",
    )
    payment_intent_reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )
    source_app = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Originating app name, e.g. payments, refunds, payouts.",
    )
    source_model = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )
    source_object_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    mismatch_reason = models.TextField(
        blank=True,
        default="",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_ledger_reconciliations",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    reconciled_at = models.DateTimeField(
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
        db_table = "ledger_reconciliation_records"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "currency"]),
            models.Index(fields=["website", "reference"]),
            models.Index(fields=["website", "external_reference"]),
            models.Index(fields=["website", "payment_intent_reference"]),
            models.Index(fields=["website", "source_app"]),
            models.Index(fields=["website", "source_model", "source_object_id"]),
            models.Index(fields=["website", "reconciled_at"]),
            models.Index(fields=["website", "resolved_at"]),
        ]
        verbose_name = "Reconciliation Record"
        verbose_name_plural = "Reconciliation Records"

    def __str__(self) -> str:
        return (
            f"{self.reference or self.external_reference or self.id} | "
            f"{self.status}"
        )

    @property
    def is_unreconciled(self) -> bool:
        return self.status == ReconciliationStatus.UNRECONCILED

    @property
    def is_matched(self) -> bool:
        return self.status == ReconciliationStatus.MATCHED

    @property
    def is_partially_matched(self) -> bool:
        return self.status == ReconciliationStatus.PARTIALLY_MATCHED

    @property
    def is_mismatched(self) -> bool:
        return self.status == ReconciliationStatus.MISMATCHED

    @property
    def is_resolved(self) -> bool:
        return self.status == ReconciliationStatus.RESOLVED

    @property
    def is_final(self) -> bool:
        return self.status in {
            ReconciliationStatus.MATCHED,
            ReconciliationStatus.RESOLVED,
        }

    def mark_matched(self, matched_amount: Decimal | None = None) -> None:
        resolved_amount = matched_amount or self.expected_amount
        self.status = ReconciliationStatus.MATCHED
        self.actual_amount = resolved_amount
        self.matched_amount = resolved_amount
        self.variance_amount = Decimal("0.00")
        self.reconciled_at = timezone.now()
        self.mismatch_reason = ""

    def mark_partially_matched(self, matched_amount: Decimal) -> None:
        actual_amount = self.actual_amount or Decimal("0.00")
        self.status = ReconciliationStatus.PARTIALLY_MATCHED
        self.matched_amount = matched_amount
        self.variance_amount = self.expected_amount - actual_amount
        self.mismatch_reason = self.mismatch_reason or "Partial match detected."

    def mark_mismatched(self, reason: str) -> None:
        actual_amount = self.actual_amount or Decimal("0.00")
        self.status = ReconciliationStatus.MISMATCHED
        self.mismatch_reason = reason
        self.variance_amount = self.expected_amount - actual_amount

    def mark_resolved(self, resolved_by=None) -> None:
        self.status = ReconciliationStatus.RESOLVED
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()

        if not self.reconciled_at:
            self.reconciled_at = self.resolved_at

    def clean(self) -> None:
        if self.expected_amount is None:
            raise ValidationError(
                {"expected_amount": "Expected amount is required."}
            )

        if self.expected_amount <= Decimal("0.00"):
            raise ValidationError(
                {"expected_amount": "Expected amount must be greater than zero."}
            )

        if self.actual_amount is not None and self.actual_amount < Decimal("0.00"):
            raise ValidationError(
                {"actual_amount": "Actual amount cannot be negative."}
            )

        if self.matched_amount < Decimal("0.00"):
            raise ValidationError(
                {"matched_amount": "Matched amount cannot be negative."}
            )

        if self.status == ReconciliationStatus.RESOLVED and not self.resolved_at:
            raise ValidationError(
                {"resolved_at": "Resolved records must have a resolved time."}
            )