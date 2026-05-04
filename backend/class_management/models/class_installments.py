from __future__ import annotations

from decimal import Decimal

from django.db import models

from class_management.constants import ClassInstallmentStatus


class ClassInstallmentPlan(models.Model):
    """
    Payment schedule for a class order.
    """

    class_order = models.OneToOneField(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="installment_plan",
    )

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    installment_count = models.PositiveIntegerField(default=1)
    allow_work_before_full_payment = models.BooleanField(default=True)
    pause_work_when_overdue = models.BooleanField(default=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ClassInstallment(models.Model):
    """
    One scheduled payment inside an installment plan.
    """

    plan = models.ForeignKey(
        "class_management.ClassInstallmentPlan",
        on_delete=models.CASCADE,
        related_name="installments",
    )

    label = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=30,
        choices=ClassInstallmentStatus.choices,
        default=ClassInstallmentStatus.PENDING,
        db_index=True,
    )

    due_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)

    invoice_id = models.CharField(max_length=120, blank=True)
    payment_intent_id = models.CharField(max_length=120, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at"]
        indexes = [
            models.Index(fields=["status", "due_at"]),
        ]