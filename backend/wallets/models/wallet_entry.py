from decimal import Decimal
from typing import cast, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from wallets.constants import (
    WalletEntryDirection,
    WalletEntryStatus,
    WalletEntryType,
)


class WalletEntry(models.Model):
    """
    Immutable wallet movement record.

    Each balance affecting event should create a WalletEntry.
    Posted entries should not be edited. Use reversal or compensating entries.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="wallet_entries",
    )
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.CASCADE,
        related_name="entries",
    )
    ledger_transaction = models.ForeignKey(
        "ledger.LedgerTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_entries",
    )
    entry_type = models.CharField(
        max_length=50,
        choices=WalletEntryType.choices,
    )
    direction = models.CharField(
        max_length=10,
        choices=WalletEntryDirection.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=WalletEntryStatus.choices,
        default=WalletEntryStatus.POSTED,
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    balance_before = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    balance_after = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    description = models.TextField(
        blank=True,
        default="",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_wallet_entries",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "wallets_wallet_entry"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["website", "wallet"]),
            models.Index(fields=["entry_type", "status"]),
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"WalletEntry<{self.pk}> "
            f"wallet={cast(Any, self).wallet_id} "
            f"{self.direction} "
            f"{self.amount}"
        )

    def clean(self) -> None:
        if self.amount <= 0:
            raise ValidationError({"amount": "Amount must be greater than zero."})

        if cast(Any, self).wallet_id and cast(Any, self).website_id and self.wallet.website_id != cast(Any, self).website_id:
            raise ValidationError(
                {"website": "Wallet entry website must match wallet website."}
            )