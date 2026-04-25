from __future__ import annotations
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import (
    OrderAdjustmentStatus,
    OrderAdjustmentType,
    OrderScopeUnitType,
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
    unit_type = models.CharField(
        max_length=32,
        choices=OrderScopeUnitType.choices,
        default=OrderScopeUnitType.OTHER,
        help_text="Unit type for the requested change.",
    )
    adjustment_kind = models.CharField(
        max_length=32,
        default="scope_increment",
        help_text="Granular kind of adjustment, e.g. scope_increment or extra_service.",
    )
    extra_service_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="Code representing the extra service if adjustment_kind is extra_service.",
    )
    writer_justification = models.TextField(
        blank=True,
        help_text="Writer or staff justification for the request.",
    )
    last_client_response_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last client response reminder was sent.",
    )
    last_writer_counter_response_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    last_staff_resolution_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
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
    current_quantity = models.PositiveBigIntegerField(
        default=0,
        help_text="Current scope quantity of the order."
    )
    requested_quantity = models.PositiveBigIntegerField(
        default=0,
        help_text="Quantity requested by the writer."
    )
    quantity_delta = models.PositiveBigIntegerField(
        default=0,
        help_text="Requested increment above the current quantity."
    )
    countered_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Counter proposal quantity if client issued a counter.",
    )
    countered_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Counter proposal deadline if client issued a counter.",
    )
    countered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="countered_order_adjustment_requests",
        null=True,
        blank=True,
        help_text="Actor who issued the counter proposal.",
    )
    is_counter_final = models.BooleanField(
        default=False,
        help_text="Whether the client's counter proposal is marked as final.",
    )
    client_visible_note = models.TextField(
        blank=True,
        default="",
        help_text="Message shown to the client.",
    )
    countered_note = models.TextField(
        blank=True,
        default="",
        help_text="Counter proposal note if client issued a counter.",
    )
    request_pricing_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pricing payload for the writer request.",
    )
    counter_pricing_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Pricing payload for the client counter.",
    )
    request_total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    counter_total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    request_writer_compensation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    counter_writer_compensation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    source_pricing_snapshot = models.ForeignKey(
        "order_pricing_core.PricingSnapshot",
        on_delete=models.SET_NULL,
        related_name="adjustment_requests",
        null=True,
        blank=True,
    )
    counter_pricing_snapshot = models.ForeignKey(
        "order_pricing_core.PricingSnapshot",
        on_delete=models.SET_NULL,
        related_name="counter_adjustment_requests",
        null=True,
        blank=True,
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    resolved_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="resolved_order_adjustments",
        null=True,
        blank=True,
    )    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the client response window expires.",
    )
    escalated_after_counter = models.BooleanField(
        default=False,
        help_text="Whether writer escalated after funded counter was applied.",
    )
    escalation_reason = models.TextField(
        blank=True,
        default="",
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
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the accepted request was applied to the order.",
    )

    class Meta:
        """
        Configure ordering and indexes for adjustment requests.
        """
        db_table = "orders_order_adjustment_request"
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

        if self.counter_pricing_snapshot and not self.counter_pricing_payload:
            raise ValidationError(
                "counter_pricing_payload must be set if counter_pricing_snapshot is set."
            )
        
        if self.countered_quantity is not None:
            if self.countered_quantity <= self.current_quantity:
                raise ValidationError(
                    "countered_quantity must be greater than current_quantity."
                )
            if self.countered_quantity > self.requested_quantity:
                raise ValidationError(
                    "countered_quantity cannot be greater than requested_quantity."
                )

        if self.adjustment_kind == "scope_increment":
            if not self.unit_type:
                raise ValidationError(
                    "unit_type is required."
                )
            if self.requested_quantity <= self.current_quantity:
                raise ValidationError(
                    "requested_quantity must be greater than current_quantity for scope_increment adjustments."
                )
            
            if self.quantity_delta != self.requested_quantity - self.current_quantity:
                raise ValidationError(
                    "quantity_delta must equal requested_quantity minus current_quantity for scope_increment adjustments."
                )
            
            if self.extra_service_code:
                raise ValidationError(
                    "extra_service_code must be empty when adjustment_kind is scope_increment."
                )
            
            if self.quantity_delta <= 0:
                raise ValidationError(
                    "quantity_delta must be greater than 0 for scope_increment adjustments."
                )

        if self.adjustment_kind == "extra_service":
            if not self.extra_service_code:
                raise ValidationError(
                    "extra_service_code must be set when adjustment_kind is extra_service."
                )