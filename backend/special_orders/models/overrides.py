from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    AdminOverrideStatus,
    AdminOverrideType,
)


class SpecialOrderAdminOverride(TimeStampedModel):
    """
    Auditable admin override for dangerous special order actions.

    This replaces unsafe boolean shortcuts such as:
        - admin_marked_paid
        - admin_unlocked_files
        - manual paid flags

    Financial overrides must still create payment applications,
    refund applications, wallet records, or ledger records through services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_admin_overrides",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="admin_overrides",
    )

    override_type = models.CharField(
        max_length=50,
        choices=AdminOverrideType.CHOICES,
    )
    status = models.CharField(
        max_length=50,
        choices=AdminOverrideStatus.CHOICES,
        default=AdminOverrideStatus.PENDING,
    )

    reason = models.TextField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=(
            "Optional amount for manual funding, price, or adjustment "
            "overrides."
        ),
    )
    currency = models.CharField(max_length=10, default="USD")

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_special_order_overrides",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_special_order_overrides",
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applied_special_order_overrides",
    )

    approved_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    reversed_at = models.DateTimeField(null=True, blank=True)

    payment_application = models.ForeignKey(
        "special_orders.SpecialOrderPaymentApplication",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_overrides",
        help_text=(
            "Payment application created by this override, if the override "
            "affects funding."
        ),
    )
    delivery_checkpoint = models.ForeignKey(
        "special_orders.SpecialOrderDeliveryCheckpoint",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_overrides",
        help_text=(
            "Delivery checkpoint affected by this override, if applicable."
        ),
    )
    ledger_entry_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to the ledger entry created by this override.",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "override_type"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderAdminOverride("
            f"order={self.special_order_id}, "
            f"type={self.override_type})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        payment_application_id: int | None
        delivery_checkpoint_id: int | None