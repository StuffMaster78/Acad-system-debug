from decimal import Decimal
from typing import cast, Any
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from wallets.constants import WalletHoldStatus


class WalletHold(models.Model):
    """
    Represents a temporary reservation of wallet funds.

    Useful for split payments, checkout reservations, and payout reservations.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="wallet_holds",
    )
    wallet = models.ForeignKey(
        "wallets.Wallet",
        on_delete=models.CASCADE,
        related_name="holds",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=WalletHoldStatus.choices,
        default=WalletHoldStatus.ACTIVE,
    )
    reason = models.CharField(
        max_length=255,
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
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    released_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    captured_at = models.DateTimeField(
        null=True,
        blank=True,
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
        related_name="created_wallet_holds",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "wallets_wallet_hold"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["website", "wallet"]),
            models.Index(fields=["status"]),
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"WalletHold<{self.pk}> "
            f"wallet={cast(Any, self).wallet_id} "
            f"amount={self.amount} "
            f"status={self.status}"
        )

    def clean(self) -> None:
        if self.amount <= 0:
            raise ValidationError({"amount": "Hold amount must be greater than zero."})

        if cast(Any, self).wallet_id and cast(Any, self).website_id and self.wallet.website_id != cast(Any, self).website_id:
            raise ValidationError(
                {"website": "Wallet hold website must match wallet website."}
            )