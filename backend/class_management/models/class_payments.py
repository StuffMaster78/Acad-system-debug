from __future__ import annotations

from decimal import Decimal

from django.db import models

from class_management.constants import ClassPaymentSourceType


class ClassInvoiceLink(models.Model):
    """
    Links class orders to billing invoices without owning billing logic.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="invoice_links",
    )

    invoice_id = models.CharField(max_length=120)
    invoice_number = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=60, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["class_order", "invoice_id"]),
        ]


class ClassPaymentAllocation(models.Model):
    """
    Records payment applied to a class order.

    The actual payment, wallet, and ledger entries belong to their own
    apps. This model is the class domain receipt of application.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="payment_allocations",
    )

    source_type = models.CharField(
        max_length=30,
        choices=ClassPaymentSourceType.choices,
        db_index=True,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    wallet_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    external_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    installment = models.ForeignKey(
        "class_management.ClassInstallment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_allocations",
    )

    payment_intent_id = models.CharField(max_length=120, blank=True)
    payment_transaction_id = models.CharField(max_length=120, blank=True)
    wallet_transaction_id = models.CharField(max_length=120, blank=True)
    ledger_entry_id = models.CharField(max_length=120, blank=True)

    reference = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        indexes = [
            models.Index(fields=["class_order", "source_type"]),
            models.Index(fields=["payment_intent_id"]),
            models.Index(fields=["wallet_transaction_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["payment_intent_id"],
                condition=~models.Q(payment_intent_id=""),
                name="unique_class_payment_intent_id",
            ),
            models.UniqueConstraint(
                fields=["payment_transaction_id"],
                condition=~models.Q(payment_transaction_id=""),
                name="unique_class_payment_transaction_id",
            ),
        ]