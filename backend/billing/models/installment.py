from __future__ import annotations

from decimal import Decimal
from django.db import models

from billing.models.base import BillingBaseModel


class PaymentInstallment(BillingBaseModel):
    """
    Represent an installment against a billing invoice.

    Installments break a single invoice into scheduled payable parts.
    Business rules around schedule creation and settlement belong in
    services, not in this model.
    """

    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.CASCADE,
        related_name="installments",
        help_text="Invoice to which this installment belongs.",
    )
    sequence_number = models.PositiveIntegerField(
        help_text="Installment order within the invoice schedule.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount due for this installment.",
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount already allocated to this installment.",
    )
    due_at = models.DateTimeField(
        help_text="Timestamp after which the installment is overdue.",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this installment became fully paid.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this installment was cancelled.",
    )

    class Meta(BillingBaseModel.Meta):
        """
        Configure ordering and index strategy for installments.
        """

        ordering = ("invoice_id", "sequence_number", "due_at", "created_at")
        indexes = [
            models.Index(fields=["invoice", "sequence_number"]),
            models.Index(fields=["website", "due_at"]),
            models.Index(fields=["website", "invoice"]),
            models.Index(fields=["website", "paid_at"]),
            models.Index(fields=["website", "cancelled_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "sequence_number"],
                name="unique_installment_sequence_per_invoice",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable installment representation.

        Returns:
            str: Human-readable installment description.
        """
        return (
            f"Installment {self.sequence_number} "
            f"for {self.invoice.reference}"
        )