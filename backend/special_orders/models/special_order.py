from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    SpecialOrderOrigin,
    SpecialOrderPricingMode,
    SpecialOrderPriority,
    SpecialOrderStatus,
)


class SpecialOrder(TimeStampedModel):
    """
    Root entity for fixed and quoted special orders.

    This model stores scope and lifecycle state only.

    It does not:
        1. Calculate pricing.
        2. Apply payments.
        3. Mark money as paid.
        4. Post ledger entries.
        5. Pay writers.

    Those responsibilities belong to services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_orders",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_orders",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_special_orders",
        limit_choices_to={"role": "writer"},
    )

    pricing_mode = models.CharField(
        max_length=50,
        choices=SpecialOrderPricingMode.CHOICES,
        default=SpecialOrderPricingMode.QUOTED,
    )
    status = models.CharField(
        max_length=50,
        choices=SpecialOrderStatus.CHOICES,
        default=SpecialOrderStatus.INQUIRY,
    )
    origin = models.CharField(
        max_length=50,
        choices=SpecialOrderOrigin.CHOICES,
        default=SpecialOrderOrigin.CLIENT_REQUEST,
    )
    priority = models.CharField(
        max_length=50,
        choices=SpecialOrderPriority.CHOICES,
        default=SpecialOrderPriority.NORMAL,
    )

    title = models.CharField(max_length=255)
    inquiry_details = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Client stated budget for negotiation purposes.",
    )
    duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Requested turnaround duration in days.",
    )
    currency = models.CharField(max_length=10, default="USD")

    predefined_config = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_orders",
    )
    predefined_duration = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderDuration",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_orders",
    )
    writer_pay_rule = models.ForeignKey(
        "special_orders.SpecialOrderWriterPayRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_orders",
    )

    accepted_quote = models.OneToOneField(
        "special_orders.SpecialOrderQuote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_for_order",
    )
    converted_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_special_orders",
        help_text=(
            "Optional standard order created from this special order "
            "for execution."
        ),
    )

    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "pricing_mode"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "writer"]),
            models.Index(fields=["website", "priority"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Special Order #{self.pk}"

    if TYPE_CHECKING:
        id: int
        website_id: int
        client_id: int
        writer_id: int | None
        writer_pay_rule_id: int | None


class SpecialOrderStatusHistory(TimeStampedModel):
    """
    Immutable audit trail for special order status transitions.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_status_history",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    previous_status = models.CharField(
        max_length=50,
        choices=SpecialOrderStatus.CHOICES,
        null=True,
        blank=True,
    )
    new_status = models.CharField(
        max_length=50,
        choices=SpecialOrderStatus.CHOICES,
    )
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_order_status_changes",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "new_status"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderStatusHistory("
            f"order={self.special_order_id}, "
            f"status={self.new_status})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int