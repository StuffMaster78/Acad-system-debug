from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from class_management.constants import (
    ClassWriterCompensationStatus,
    ClassWriterCompensationType,
)


class ClassWriterCompensation(models.Model):
    """
    Admin controlled writer compensation for a class order.
    """

    class_order = models.OneToOneField(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="writer_compensation",
    )

    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="class_writer_compensations",
    )

    compensation_type = models.CharField(
        max_length=30,
        choices=ClassWriterCompensationType.choices,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    fixed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
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

    status = models.CharField(
        max_length=40,
        choices=ClassWriterCompensationStatus.choices,
        default=ClassWriterCompensationStatus.DRAFT,
        db_index=True,
    )

    wallet_transaction_id = models.CharField(max_length=120, blank=True)
    ledger_entry_id = models.CharField(max_length=120, blank=True)

    admin_notes = models.TextField(blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_class_writer_compensations",
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_class_writer_compensations",
    )

    approved_at = models.DateTimeField(null=True, blank=True)
    earned_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Meta:
    constraints = [
        models.CheckConstraint(
            condition=models.Q(final_amount__gte=0),
            name="class_writer_comp_final_amount_non_negative",
        ),
        models.CheckConstraint(
            condition=models.Q(paid_amount__gte=0),
            name="class_writer_comp_paid_amount_non_negative",
        ),
    ]