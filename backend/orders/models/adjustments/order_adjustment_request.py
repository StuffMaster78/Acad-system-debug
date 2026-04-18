from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import (
    OrderAdjustmentStatus,
    OrderAdjustmentType,
)
from websites.models.websites import Website


class OrderAdjustmentRequest(models.Model):
    """
    Represent a request to change paid order scope or commercial terms.

    The request stores structured scope intent and workflow state.
    Commercial proposals, pricing snapshots, and funding records live in
    related models.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_requests",
        help_text="Tenant website that owns the adjustment request.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="adjustment_requests",
        help_text="Order affected by the adjustment request.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_order_adjustment_requests",
        null=True,
        blank=True,
        help_text="Actor who initiated the adjustment request.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_order_adjustment_requests",
        null=True,
        blank=True,
        help_text="Actor who last reviewed the request.",
    )
    adjustment_type = models.CharField(
        max_length=64,
        choices=OrderAdjustmentType.choices,
        help_text="Structured category of the requested change.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title describing the request.",
    )
    description = models.TextField(
        blank=True,
        help_text="Customer facing description of the request.",
    )
    writer_justification = models.TextField(
        blank=True,
        help_text="Writer or staff justification for the request.",
    )
    requested_scope_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured payload describing requested scope delta.",
    )
    accepted_proposal = models.ForeignKey(
        "orders.OrderAdjustmentProposal",
        on_delete=models.SET_NULL,
        related_name="accepted_by_adjustment_requests",
        null=True,
        blank=True,
        help_text="Proposal that became commercially binding.",
    )
    current_proposal = models.ForeignKey(
        "orders.OrderAdjustmentProposal",
        on_delete=models.SET_NULL,
        related_name="current_for_adjustment_requests",
        null=True,
        blank=True,
        help_text="Latest active proposal in the negotiation.",
    )
    status = models.CharField(
        max_length=32,
        choices=OrderAdjustmentStatus.choices,
        default=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
        help_text="Current lifecycle state of the request.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the client response window expires.",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was commercially accepted.",
    )
    declined_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was declined.",
    )
    countered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the client issued a counter proposal.",
    )
    funded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request became fully funded.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was cancelled.",
    )
    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the funded request was reversed.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the request was last updated.",
    )

    class Meta:
        """
        Configure ordering and indexes for adjustment requests.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["requested_by", "status"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable adjustment request description.

        Returns:
            str:
                Human readable request representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return (
            f"OrderAdjustmentRequest id={self.pk} "
            f"order={order_pk}"
        )

    def clean(self) -> None:
        """
        Validate adjustment request invariants.

        Raises:
            ValidationError:
                Raised when website or proposal linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Adjustment website must match order website."
                )

        if self.accepted_proposal is not None:
            if self.accepted_proposal.adjustment_request is None:
                raise ValidationError(
                    "Accepted proposal must belong to a request."
                )

            if self.pk is not None:
                if self.accepted_proposal.adjustment_request.pk != self.pk:
                    raise ValidationError(
                        "Accepted proposal must belong to this request."
                    )

        if self.current_proposal is not None:
            if self.current_proposal.adjustment_request is None:
                raise ValidationError(
                    "Current proposal must belong to a request."
                )

            if self.pk is not None:
                if self.current_proposal.adjustment_request.pk != self.pk:
                    raise ValidationError(
                        "Current proposal must belong to this request."
                    )