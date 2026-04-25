from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import (
    OrderAdjustmentProposalRole,
    OrderAdjustmentProposalType,
    OrderScopeUnitType,
)
from websites.models.websites import Website


class OrderAdjustmentProposal(models.Model):
    """
    Represent a commercial proposal inside an adjustment negotiation.

    Each negotiation step gets its own proposal row. This avoids
    flattening counters and overrides onto the adjustment root.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_proposals",
        help_text="Tenant website that owns this proposal.",
    )
    adjustment_request = models.ForeignKey(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="proposals",
        help_text="Adjustment request this proposal belongs to.",
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_adjustment_proposals",
        null=True,
        blank=True,
        help_text="Actor who created the proposal.",
    )
    proposal_role = models.CharField(
        max_length=16,
        choices=OrderAdjustmentProposalRole.choices,
        help_text="Role of the proposing actor.",
    )
    proposal_type = models.CharField(
        max_length=32,
        choices=OrderAdjustmentProposalType.choices,
        help_text="Type of commercial proposal.",
    )
    unit_type = models.CharField(
        max_length=32,
        choices=OrderScopeUnitType.choices,
        default=OrderScopeUnitType.OTHER,
        help_text=(
            "Unit type for the proposed adjustment"
            "(e.g. Slides, Diagrams, Design, Pages)."
        ),
    )
    adjustment_kind = models.CharField(
        max_length=32,
        blank=True,
        help_text="Kind of adjustment (e.g. Credit, Refund, Rebill).",
    )
    currency = models.CharField(
        max_length=8,
        default="",
        help_text="Currency for the proposal amount.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Commercial amount proposed for the adjustment.",
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason supplied for the proposal.",
    )
    scope_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Scope payload associated with this proposal.",
    )
    pricing_snapshot_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pricing calculation payload for this proposal.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the proposal is still active.",
    )
    supersedes_proposal = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="superseded_by",
        null=True,
        blank=True,
        help_text="Previous proposal this proposal supersedes.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the proposal was created.",
    )

    class Meta:
        """
        Configure ordering, indexes, and constraints for proposals.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "adjustment_request"]),
            models.Index(fields=["adjustment_request", "is_active"]),
            models.Index(fields=["proposal_type", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="orders_adj_proposal_amount_gt_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable proposal description.

        Returns:
            str:
                Human readable proposal representation.
        """
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderAdjustmentProposal id={self.pk} "
            f"request={request_pk}"
        )

    def clean(self) -> None:
        """
        Validate proposal invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.adjustment_request is not None and self.website is not None:
            if self.website.pk != self.adjustment_request.website.pk:
                raise ValidationError(
                    "Proposal website must match adjustment website."
                )

        if self.supersedes_proposal is not None:
            if self.adjustment_request is None:
                raise ValidationError(
                    "Superseded proposal requires an adjustment request."
                )

            if self.supersedes_proposal.adjustment_request is None:
                raise ValidationError(
                    "Superseded proposal must belong to a request."
                )

            if (
                self.supersedes_proposal.adjustment_request.pk
                != self.adjustment_request.pk
            ):
                raise ValidationError(
                    "Superseded proposal must belong to same request."
                )