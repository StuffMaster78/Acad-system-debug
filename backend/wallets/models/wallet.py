from decimal import Decimal
from typing import Any, cast
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from wallets.constants import WalletStatus, WalletType


class Wallet(models.Model):
    """
    Stores wallet level balances for a tenant scoped owner.

    Balance fields are cached values for fast reads.
    WalletEntry remains the money movement source of truth.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets",
    )
    wallet_type = models.CharField(
        max_length=20,
        choices=WalletType.choices,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    status = models.CharField(
        max_length=20,
        choices=WalletStatus.choices,
        default=WalletStatus.ACTIVE,
    )
    available_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    pending_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_credited = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_debited = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    last_activity_at = models.DateTimeField(
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
        db_table = "wallets_wallet"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "owner_user", "wallet_type", "currency"],
                name="wallets_unique_wallet_per_owner_type_currency",
            ),
            models.CheckConstraint(
                condition=models.Q(available_balance__gte=0),
                name="wallets_available_balance_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(pending_balance__gte=0),
                name="wallets_pending_balance_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(total_credited__gte=0),
                name="wallets_total_credited_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(total_debited__gte=0),
                name="wallets_total_debited_gte_0",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "owner_user"]),
            models.Index(fields=["wallet_type", "status"]),
            models.Index(fields=["currency"]),
        ]

    def __str__(self) -> str:
        return (
            f"Wallet<{cast(Any, self).id}> "
            f"user={cast(Any, self).owner_user_id} "
            f"type={self.wallet_type} "
            f"currency={self.currency}"
        )

    def clean(self) -> None:
        if self.available_balance < 0:
            raise ValidationError(
                {"available_balance": "Available balance cannot be negative."}
            )

        if self.pending_balance < 0:
            raise ValidationError(
                {"pending_balance": "Pending balance cannot be negative."}
            )

        if self.total_credited < 0:
            raise ValidationError(
                {"total_credited": "Total credited cannot be negative."}
            )

        if self.total_debited < 0:
            raise ValidationError(
                {"total_debited": "Total debited cannot be negative."}
            )

    @property
    def is_active(self) -> bool:
        return self.status == WalletStatus.ACTIVE