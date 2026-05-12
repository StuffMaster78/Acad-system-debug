from __future__ import annotations

from decimal import Decimal

from django.db import models

from writer_compensation.models.compensation_event import (
    CompensationEvent,
)


class FinancialEventItem(models.Model):
    """
    Atomic compensation breakdown unit attached to a CompensationEvent.

    Each item represents a single source of value in a compensation cycle.

    Rules:
        1. total_amount MUST equal quantity * unit_amount.
        2. Each item MUST belong to exactly one financial event.
        3. Items are immutable once settled.
    """

    class ItemType(models.TextChoices):
        ORDER = "order", "Order"
        SPECIAL_ORDER = "special_order", "Special Order"
        CLASS = "class", "Class"
        TIP = "tip", "Tip"
        BONUS = "bonus", "Bonus"
        ADJUSTMENT = "adjustment", "Adjustment"
        DEDUCTION = "deduction", "Deduction"
        OTHER = "other", "Other"

    compensation_event = models.ForeignKey(
        CompensationEvent,
        on_delete=models.CASCADE,
        related_name="items",
    )

    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
    )

    unit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    # Strong relational integrity instead of raw IDs
    order = models.ForeignKey(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="compensation_items",
    )

    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="compensation_items",
    )

    class_session = models.ForeignKey(
        "classes.ClassSession",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="compensation_items",
    )

    is_locked = models.BooleanField(
        default=False,
        help_text="Locked after settlement to prevent modifications",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def clean(self) -> None:
        """
        Enforce deterministic financial consistency.
        """
        expected = self.quantity * self.unit_amount

        if self.total_amount != expected:
            raise ValueError(
                "total_amount must equal quantity * unit_amount"
            )

    def lock(self) -> None:
        """
        Prevent further modifications after settlement.
        """
        self.is_locked = True
        self.save(update_fields=["is_locked"])

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["item_type"]),
            models.Index(fields=["financial_event"]),
        ]

    def __str__(self) -> str:
        return f"{self.item_type} | {self.title} | {self.total_amount}"
