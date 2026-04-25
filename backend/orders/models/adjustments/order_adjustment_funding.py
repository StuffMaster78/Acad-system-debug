from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderAdjustmentFundingStatus
from websites.models.websites import Website


class OrderAdjustmentFunding(models.Model):
    """
    Represent the billing and payment linkage for an adjustment.

    Billing owns receivables.
    Payments processor owns settlement.
    Ledger owns money movement.
    This model stores correlation and state for the adjustment side.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_fundings",
        help_text="Tenant website that owns this funding record.",
    )
    adjustment_request = models.OneToOneField(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="funding",
        help_text="Adjustment request this funding record belongs to.",
    )
    billing_payment_request = models.ForeignKey(
        "billing.PaymentRequest",
        on_delete=models.SET_NULL,
        related_name="order_adjustment_fundings",
        null=True,
        blank=True,
        help_text="Billing payment request linked to the adjustment.",
    )
    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.SET_NULL,
        related_name="order_adjustment_fundings",
        null=True,
        blank=True,
        help_text="Billing invoice linked to the adjustment, if any.",
    )
    status = models.CharField(
        max_length=32,
        choices=OrderAdjustmentFundingStatus.choices,
        default=OrderAdjustmentFundingStatus.NOT_STARTED,
        help_text="Funding lifecycle status.",
    )
    payment_request_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Billing layer payment request reference.",
    )
    payment_intent_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="External payment intent reference.",
    )
    external_reference = models.CharField(
        max_length=128,
        blank=True,
        default="",
    )
    funding_reference = models.CharField(
        max_length=128,
        blank=True,
        help_text="Internal reference for funding orchestration.",
    )
    invoice_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Invoice reference associated with this funding flow.",
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When funding is due.",
    )
    amount_expected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total amount expected before funding is complete.",
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total amount applied so far.",
    )
    funded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When funding fully completed.",
    )
    last_funding_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last funding reminder was sent.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured funding metadata.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the funding record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the funding record was last updated.",
    )

    class Meta:
        """
        Configure indexes for funding records.
        """
        db_table = "orders_order_adjustment_funding"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["payment_request_reference"]),
            models.Index(fields=["payment_intent_reference"]),
            models.Index(fields=["invoice_reference"]),
            models.Index(fields=["funding_reference"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable funding description.

        Returns:
            str:
                Human readable funding representation.
        """
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderAdjustmentFunding request={request_pk} "
            f"status={self.status}"
        )

    def clean(self) -> None:
        """
        Validate funding invariants.

        Raises:
            ValidationError:
                Raised when website linkage or funding values are invalid.
        """
        super().clean()

        if self.adjustment_request is not None and self.website is not None:
            if self.website.pk != self.adjustment_request.website.pk:
                raise ValidationError(
                    "Funding website must match adjustment website."
                )

        if self.amount_expected < Decimal("0.00"):
            raise ValidationError(
                "amount_expected cannot be negative."
            )

        if self.amount_paid < Decimal("0.00"):
            raise ValidationError(
                "amount_paid cannot be negative."
            )

        if (
            self.amount_expected > Decimal("0.00")
            and self.amount_paid > self.amount_expected
            and self.status != OrderAdjustmentFundingStatus.FUNDED
        ):
            raise ValidationError(
                "Overpaid funding records must be marked as funded."
            )