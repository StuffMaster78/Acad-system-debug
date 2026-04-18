from __future__ import annotations

from django.conf import settings
from django.db import models

from websites.models.websites import Website


class OrderAdjustmentType(models.TextChoices):
    """
    Enumerate supported order adjustment categories.

    These categories describe why the order scope or commercial terms
    changed.
    """

    PAGE_INCREASE = "page_increase", "Page Increase"
    SLIDE_INCREASE = "slide_increase", "Slide Increase"
    DEADLINE_DECREASE = "deadline_decrease", "Deadline Decrease"
    EXTRA_SERVICE = "extra_service", "Extra Service"
    OTHER = "other", "Other"


class OrderAdjustmentStatus(models.TextChoices):
    """
    Enumerate lifecycle states for an order adjustment request.

    The status tracks negotiation and funding progress within the order
    domain.
    """

    PENDING_CLIENT_RESPONSE = (
        "pending_client_response",
        "Pending Client Response",
    )
    CLIENT_COUNTERED = "client_countered", "Client Countered"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    CANCELLED = "cancelled", "Cancelled"
    FUNDING_PENDING = "funding_pending", "Funding Pending"
    FUNDED = "funded", "Funded"
    EXPIRED = "expired", "Expired"


class OrderAdjustmentRequest(models.Model):
    """
    Represent a writer or staff initiated request to adjust order scope
    or pricing.

    This model belongs to the orders domain. It tracks the negotiation
    lifecycle and final commercial decision. It does not collect money.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_requests",
        help_text="Tenant context that owns the adjustment request.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="adjustment_requests",
        help_text="Order affected by this adjustment request.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_order_adjustment_requests",
        help_text="Actor who initiated the adjustment request.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_order_adjustment_requests",
        help_text="Actor who reviewed or finalized the request.",
    )
    adjustment_type = models.CharField(
        max_length=50,
        choices=OrderAdjustmentType.choices,
        help_text="Type of scope or commercial change requested.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title describing the requested change.",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed explanation of the requested change.",
    )
    writer_justification = models.TextField(
        blank=True,
        help_text="Reason supplied by the writer or staff member.",
    )
    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Initial amount requested for the adjustment.",
    )
    client_counter_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount proposed by the client in a counter offer.",
    )
    client_counter_reason = models.TextField(
        blank=True,
        help_text="Explanation supplied by the client for a counter.",
    )
    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final agreed amount to be billed.",
    )
    status = models.CharField(
        max_length=30,
        choices=OrderAdjustmentStatus.choices,
        default=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
        help_text="Current negotiation and funding state.",
    )
    billing_payment_request = models.ForeignKey(
        "billing.PaymentRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_adjustment_requests",
        help_text="Billing payment request created from this adjustment.",
    )
    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_adjustment_requests",
        help_text="Invoice created from this adjustment, if any.",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the client accepted the request.",
    )
    declined_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the client declined the request.",
    )
    countered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the client countered the request.",
    )
    funded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the agreed amount became funded.",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional expiry timestamp for client response.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the request was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the request was last updated.",
    )

    class Meta:
        """
        Configure ordering and index strategy for adjustment requests.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable representation of the adjustment request.

        Returns:
            str: Human-readable adjustment request description.
        """
        order = self.order
        return (
            f"OrderAdjustmentRequest {self.pk} "
            f"for order {order.pk}"
        )