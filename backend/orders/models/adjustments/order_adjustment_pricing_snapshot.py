from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderAdjustmentPricingSnapshot(models.Model):
    """
    Persist pricing evidence for an adjustment proposal or request.

    This snapshot explains how the adjustment amount was computed.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_pricing_snapshots",
        help_text="Tenant website that owns this pricing snapshot.",
    )
    adjustment_request = models.ForeignKey(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="pricing_snapshots",
        help_text="Adjustment request this snapshot belongs to.",
    )
    proposal = models.ForeignKey(
        "orders.OrderAdjustmentProposal",
        on_delete=models.SET_NULL,
        related_name="pricing_snapshots",
        null=True,
        blank=True,
        help_text="Proposal this pricing snapshot was generated for.",
    )
    currency = models.CharField(
        max_length=8,
        default="",
        help_text="Currency used for the pricing snapshot.",
    )
    pricing_policy_version = models.CharField(
        max_length=64,
        blank=True,
        help_text="Pricing policy version used for the calculation.",
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Base computed amount before overrides.",
    )
    computed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final computed amount for the proposal.",
    )
    pricing_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed pricing breakdown payload.",
    )
    compensation_preview_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Projected compensation impact payload.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the pricing snapshot was created.",
    )

    class Meta:
        """
        Configure ordering, indexes, and constraints.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "adjustment_request"]),
            models.Index(fields=["adjustment_request", "proposal"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_amount__gte=0),
                name="orders_adj_price_snap_base_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(computed_amount__gte=0),
                name="orders_adj_price_snap_computed_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable pricing snapshot description.

        Returns:
            str:
                Human readable snapshot representation.
        """
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderAdjustmentPricingSnapshot "
            f"request={request_pk}"
        )

    def clean(self) -> None:
        """
        Validate pricing snapshot invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if (
            self.adjustment_request is not None
            and self.website is not None
            and self.website.pk != self.adjustment_request.website.pk
        ):
            raise ValidationError(
                "Pricing snapshot website must match adjustment website."
            )

        if self.proposal is not None:
            if self.adjustment_request is None:
                raise ValidationError(
                    "Proposal cannot be set without a request."
                )

            if self.proposal.adjustment_request is None:
                raise ValidationError(
                    "Pricing snapshot proposal must belong to a request."
                )

            if (
                self.proposal.adjustment_request.pk
                != self.adjustment_request.pk
            ):
                raise ValidationError(
                    "Pricing snapshot proposal must match request."
                )