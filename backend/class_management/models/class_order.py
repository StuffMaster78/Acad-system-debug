from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from class_management.constants import (
    ClassComplexityLevel,
    ClassOrderStatus,
    ClassPaymentStatus,
)


class ClassOrder(models.Model):
    """
    A negotiated per class academic support engagement.

    This replaces bundle first thinking. One class order represents one
    client class, its workload, access needs, pricing, payments, writer
    assignment, and completion lifecycle.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="class_orders",
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="client_class_orders",
    )

    assigned_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_class_orders",
    )

    title = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255, blank=True)
    institution_state = models.CharField(max_length=120, blank=True)

    class_name = models.CharField(max_length=255, blank=True)
    class_code = models.CharField(max_length=120, blank=True)
    class_subject = models.CharField(max_length=180, blank=True)

    academic_level = models.CharField(max_length=120, blank=True)

    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=40,
        choices=ClassOrderStatus.choices,
        default=ClassOrderStatus.DRAFT,
        db_index=True,
    )

    payment_status = models.CharField(
        max_length=40,
        choices=ClassPaymentStatus.choices,
        default=ClassPaymentStatus.UNPAID,
        db_index=True,
    )

    complexity_level = models.CharField(
        max_length=30,
        choices=ClassComplexityLevel.choices,
        default=ClassComplexityLevel.MEDIUM,
    )

    initial_client_notes = models.TextField(blank=True)
    writer_visible_notes = models.TextField(blank=True)
    admin_internal_notes = models.TextField(blank=True)

    quoted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    accepted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount_code = models.CharField(
        max_length=80,
        blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    balance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    currency = models.CharField(max_length=10, default="USD")
    latest_proposal = models.ForeignKey(
        "class_management.ClassPriceProposal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    pricing_snapshot = models.JSONField(default=dict, blank=True)
    pricing_version = models.PositiveIntegerField(default=1)
    discount_snapshot = models.JSONField(default=dict, blank=True)
    is_fully_funded = models.BooleanField(default=False)
    price_proposed_at = models.DateTimeField(null=True, blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    is_work_paused = models.BooleanField(default=False)
    pause_reason = models.CharField(max_length=120, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_orders",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_class_orders",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "assigned_writer"]),
            models.Index(fields=["payment_status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(currency=""),
                name="class_order_currency_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.client.pk})"

    def refresh_balance(self, *, save: bool = True) -> None:
        """
        Recalculate the remaining payable amount.
        """
        balance = self.final_amount - self.paid_amount
        self.balance_amount = max(balance, Decimal("0.00"))

        if self.balance_amount <= Decimal("0.00") and self.final_amount > 0:
            self.payment_status = ClassPaymentStatus.PAID
        elif self.paid_amount > Decimal("0.00"):
            self.payment_status = ClassPaymentStatus.PARTIALLY_PAID
        else:
            self.payment_status = ClassPaymentStatus.UNPAID

        if save:
            self.save(
                update_fields=[
                    "balance_amount",
                    "payment_status",
                    "updated_at",
                ]
            )

    def mark_submitted(self) -> None:
        """
        Mark the order as submitted by the client.
        """
        self.status = ClassOrderStatus.SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=["status", "submitted_at", "updated_at"])