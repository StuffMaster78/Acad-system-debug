from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from billing.constants import (
    PaymentRequestPurpose,
    PaymentRequestStatus,
)
from billing.models.base import BillingBaseModel


def generate_payment_request_reference() -> str:
    """
    Generate a short human-readable payment request reference.

    Returns:
        str: Uppercase alphanumeric reference string.
    """
    return uuid.uuid4().hex[:10].upper()


class PaymentRequest(BillingBaseModel):
    """
    Represent a customer-facing payment request.

    A payment request is a generic receivable record that can be used
    independently or as a precursor to invoice-driven payment flow.
    """

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payment_requests",
        help_text="Linked user recipient when the recipient exists.",
    )
    recipient_email = models.EmailField(
        blank=True,
        help_text="Fallback recipient email when no client is linked.",
    )
    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Display name for the payment request recipient.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_billing_payment_requests",
        help_text="Actor who created the payment request.",
    )
    reference = models.CharField(
        max_length=32,
        unique=True,
        default=generate_payment_request_reference,
        editable=False,
        help_text="Unique payment request reference.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title describing the payment request.",
    )
    purpose = models.CharField(
        max_length=50,
        choices=PaymentRequestPurpose.choices,
        default=PaymentRequestPurpose.OTHER,
        help_text="Structured business purpose of the request.",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed customer-facing request description.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payment_requests",
        help_text="Optional linked order.",
    )
    order_adjustment_request = models.ForeignKey(
        "orders.OrderAdjustmentRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payment_requests",
        help_text="Order adjustment request that produced this receivable.",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payment_requests",
        help_text="Optional linked special order.",
    )
    class_purchase = models.ForeignKey(
        "class_management.ClassPurchase",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_payment_requests",
        help_text="Optional linked class purchase.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total amount requested from the recipient.",
    )
    currency = models.CharField(
        max_length=10,
        blank=True,
        help_text="Currency code used for the request amount.",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentRequestStatus.choices,
        default=PaymentRequestStatus.DRAFT,
        help_text="Current lifecycle state of the payment request.",
    )
    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the payment request was issued.",
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional due timestamp for the request.",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request became fully paid.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request was cancelled.",
    )
    expired_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request expired.",
    )
    payment_token = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        help_text="Secure token used for payment request access.",
    )
    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration timestamp for the payment request token.",
    )
    payment_intent_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Linked payment intent reference from the processor.",
    )
    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_payment_requests",
        help_text="Optional invoice created from this request.",
    )

    class Meta(BillingBaseModel.Meta):
        """
        Configure payment request ordering and indexes.

        Indexes target common tenant-scoped and status-scoped reads.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["payment_intent_reference"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable payment request representation.

        Returns:
            str: Human-readable payment request reference.
        """
        return f"PaymentRequest {self.reference}"