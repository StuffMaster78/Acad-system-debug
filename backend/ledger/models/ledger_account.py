from __future__ import annotations

from django.core.validators import MinLengthValidator
from django.db import models

from ledger.constants import LedgerAccountStatus, LedgerAccountType


class LedgerAccount(models.Model):
    """
    Represents a financial account in the ledger.

    Examples:
        PLATFORM_CASH
        GATEWAY_CLEARING
        CLIENT_WALLET_LIABILITY
        WRITER_PAYABLE
        PLATFORM_REVENUE
        FINES_RECOVERY
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="ledger_accounts",
    )
    code = models.CharField(
        max_length=64,
        validators=[MinLengthValidator(2)],
        help_text="Stable internal account code, e.g. PLATFORM_CASH.",
    )
    name = models.CharField(
        max_length=255,
        help_text="Human friendly ledger account name.",
    )
    account_type = models.CharField(
        max_length=20,
        choices=LedgerAccountType.choices,
    )
    currency = models.CharField(
        max_length=10,
        default="KES",
        help_text="ISO currency code, e.g. KES, USD.",
    )
    status = models.CharField(
        max_length=20,
        choices=LedgerAccountStatus.choices,
        default=LedgerAccountStatus.ACTIVE,
    )

    is_system_account = models.BooleanField(
        default=False,
        help_text="Whether this account is platform controlled.",
    )
    allows_negative = models.BooleanField(
        default=False,
        help_text="Whether balances on this account may go negative.",
    )

    description = models.TextField(
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
        db_table = "ledger_accounts"
        ordering = ["website_id", "account_type", "code"]
        unique_together = [
            ("website", "code"),
        ]
        indexes = [
            models.Index(fields=["website", "code"]),
            models.Index(fields=["website", "account_type"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "is_system_account"]),
        ]
        verbose_name = "Ledger Account"
        verbose_name_plural = "Ledger Accounts"

    def __str__(self) -> str:
        return f"{self.code} ({self.name})"

    @property
    def is_active(self) -> bool:
        return self.status == LedgerAccountStatus.ACTIVE

    def deactivate(self) -> None:
        self.status = LedgerAccountStatus.INACTIVE

    def archive(self) -> None:
        self.status = LedgerAccountStatus.ARCHIVED