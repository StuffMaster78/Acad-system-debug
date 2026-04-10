from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ledger.constants import (
    JournalEntryStatus,
    LedgerEntryType,
    SourceApp,
)


class JournalEntry(models.Model):
    """
    Represents a single financial event in the ledger.

    A journal entry is the parent container for one or more journal lines.
    The lines inside the entry must balance:
        total debits == total credits

    Examples:
        wallet top up
        order payment
        split payment capture
        writer earning accrual
        refund to wallet
        dispute hold
        manual adjustment
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="journal_entries",
    )
    entry_number = models.CharField(
        max_length=64,
        unique=True,
        validators=[MinLengthValidator(4)],
        help_text="Stable human readable entry reference.",
    )
    entry_type = models.CharField(
        max_length=64,
        choices=LedgerEntryType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=JournalEntryStatus.choices,
        default=JournalEntryStatus.DRAFT,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
        help_text="ISO currency code for all lines in this entry.",
    )
    description = models.TextField(
        blank=True,
        default="",
    )
    reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Business reference such as payment ref or order ref.",
    )
    source_app = models.CharField(
        max_length=64,
        choices=SourceApp.choices,
        blank=True,
        default="",
    )
    source_model = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Source model name, e.g. OrderPayment or Refund.",
    )
    source_object_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Primary key of the source business object.",
    )
    external_reference = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Gateway/provider reference when applicable.",
    )
    payment_intent_reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Reference to the central payment intent when applicable.",
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_journal_entries",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_journal_entries",
    )
    reversal_of = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversed_by",
        help_text="Original entry that this entry reverses.",
    )
    effective_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this entry takes financial effect.",
    )
    posted_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    failure_reason = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "ledger_journal_entries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "entry_type"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "currency"]),
            models.Index(fields=["website", "reference"]),
            models.Index(fields=["website", "source_app"]),
            models.Index(fields=["website", "source_model", "source_object_id"]),
            models.Index(fields=["website", "external_reference"]),
            models.Index(fields=["website", "payment_intent_reference"]),
            models.Index(fields=["website", "effective_at"]),
            models.Index(fields=["website", "posted_at"]),
        ]
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"

    def __str__(self) -> str:
        return f"{self.entry_number} [{self.entry_type}]"

    @property
    def is_draft(self) -> bool:
        return self.status == JournalEntryStatus.DRAFT

    @property
    def is_pending(self) -> bool:
        return self.status == JournalEntryStatus.PENDING

    @property
    def is_posted(self) -> bool:
        return self.status == JournalEntryStatus.POSTED

    @property
    def is_reversed(self) -> bool:
        return self.status == JournalEntryStatus.REVERSED

    @property
    def is_failed(self) -> bool:
        return self.status == JournalEntryStatus.FAILED

    @property
    def is_final(self) -> bool:
        return self.status in {
            JournalEntryStatus.POSTED,
            JournalEntryStatus.REVERSED,
            JournalEntryStatus.FAILED,
        }

    def mark_pending(self) -> None:
        self.status = JournalEntryStatus.PENDING
        self.failure_reason = ""

    def mark_posted(self) -> None:
        self.status = JournalEntryStatus.POSTED
        self.posted_at = timezone.now()
        self.failure_reason = ""

    def mark_failed(self, reason: str) -> None:
        self.status = JournalEntryStatus.FAILED
        self.failure_reason = reason

    def mark_reversed(self) -> None:
        self.status = JournalEntryStatus.REVERSED

    def can_be_modified(self) -> bool:
        return self.status in {
            JournalEntryStatus.DRAFT,
            JournalEntryStatus.PENDING,
        }

    def clean(self) -> None:
        if self.pk and self.reversal_of and self.reversal_of.pk == self.pk:
            raise ValidationError("A journal entry cannot reverse itself.")