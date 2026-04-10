from __future__ import annotations

import uuid
from decimal import Decimal
from typing import cast
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from ledger.constants import EntrySide


class JournalLine(models.Model):
    """
    Represents a single debit or credit line within a journal entry.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="journal_lines",
    )
    journal_entry = models.ForeignKey(
        "ledger.JournalEntry",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    ledger_account = models.ForeignKey(
        "ledger.LedgerAccount",
        on_delete=models.PROTECT,
        related_name="journal_lines",
    )
    entry_side = models.CharField(
        max_length=10,
        choices=EntrySide.choices,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    description = models.TextField(
        blank=True,
        default="",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lines",
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
    )
    related_object_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ledger_journal_lines"
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["website", "journal_entry"]),
            models.Index(fields=["website", "ledger_account"]),
            models.Index(fields=["website", "entry_side"]),
            models.Index(fields=["website", "currency"]),
            models.Index(fields=["website", "user"]),
            models.Index(fields=["website", "wallet_reference"]),
            models.Index(fields=["website", "payment_intent_reference"]),
            models.Index(
                fields=["website", "related_object_type", "related_object_id"]
            ),
        ]
        verbose_name = "Journal Line"
        verbose_name_plural = "Journal Lines"

    def __str__(self) -> str:
        return (
            f"{self.journal_entry.entry_number} | "
            f"{self.entry_side.upper()} | "
            f"{self.ledger_account.code} | "
            f"{self.amount}"
        )

    @property
    def is_debit(self) -> bool:
        return self.entry_side == EntrySide.DEBIT

    @property
    def is_credit(self) -> bool:
        return self.entry_side == EntrySide.CREDIT

    def clean(self) -> None:
        if self.amount is None:
            raise ValidationError({"amount": "Amount is required."})

        if self.amount <= Decimal("0.00"):
            raise ValidationError(
                {"amount": "Amount must be greater than zero."}
            )