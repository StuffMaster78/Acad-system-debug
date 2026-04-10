from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone


class AccountBalanceSnapshot(models.Model):
    """
    Stores periodic snapshots of ledger account balances.

    Used for:
        fast balance reads
        reporting
        historical audits without recomputing from journal lines
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_balance_snapshots",
    )

    ledger_account = models.ForeignKey(
        "ledger.LedgerAccount",
        on_delete=models.CASCADE,
        related_name="balance_snapshots",
    )

    currency = models.CharField(
        max_length=10,
        default="USD",
    )

    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Computed balance at snapshot time.",
    )

    snapshot_date = models.DateTimeField(
        default=timezone.now,
        help_text="When this snapshot was taken.",
    )

    reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Optional reference (e.g. daily_close, reconciliation_run).",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "ledger_account_balance_snapshots"
        ordering = ["-snapshot_date"]
        indexes = [
            models.Index(fields=["website", "ledger_account"]),
            models.Index(fields=["website", "currency"]),
            models.Index(fields=["website", "snapshot_date"]),
            models.Index(fields=["website", "reference"]),
        ]
        verbose_name = "Account Balance Snapshot"
        verbose_name_plural = "Account Balance Snapshots"

    def __str__(self) -> str:
        return (
            f"{self.ledger_account.code} | "
            f"{self.balance} | "
            f"{self.snapshot_date}"
        )