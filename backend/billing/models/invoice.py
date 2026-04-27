from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from billing.constants import InvoicePurpose, InvoiceStatus
from websites.models.websites import Website


def generate_invoice_reference() -> str:
    """
    Generate a short, human-readable unique invoice reference.

    Returns:
        str: Uppercase alphanumeric reference identifier.
    """
    return uuid.uuid4().hex[:10].upper()


class Invoice(models.Model):
    """
    Represents a customer-facing billing document.

    An invoice defines an amount owed by a client or external recipient.
    It is part of the billing domain and should not handle payment execution
    or business workflows.

    Responsibilities:
        - Store invoice data (amount, recipient, references)
        - Track invoice state (status, timestamps)
        - Provide linkage to related business entities (orders, etc.)

    Non-responsibilities:
        - Payment processing (handled by payments_processor)
        - Business workflow transitions (handled by services)
        - Financial accounting (handled by ledger)

    Design principles:
        - Dumb model: no business logic or workflow methods
        - Multi-tenant: scoped by website
        - Flexible recipient handling (user or external email)
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="billing_invoices",
        help_text="Tenant context that owns this invoice.",
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_invoices",
        help_text="System user associated with the invoice, if applicable.",
    )

    recipient_email = models.EmailField(
        blank=True,
        help_text=(
            "Fallback email for the invoice recipient. "
            "Used when no client user is linked."
        ),
    )

    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Display name for the invoice recipient.",
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_billing_invoices",
        help_text="User who created or issued the invoice.",
    )

    reference = models.CharField(
        max_length=32,
        unique=True,
        default=generate_invoice_reference,
        editable=False,
        help_text="Unique human-readable identifier for the invoice.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Short title describing the invoice.",
    )

    purpose = models.CharField(
        max_length=50,
        choices=InvoicePurpose.choices,
        default=InvoicePurpose.OTHER,
        help_text="Structured classification of the invoice purpose.",
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed explanation of the invoice.",
    )

    order_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional display reference for external systems.",
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_invoices",
        help_text="Optional link to an order.",
    )

    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_invoices",
        help_text="Optional link to a special order.",
    )

    class_purchase = models.ForeignKey(
        "class_management.ClassPurchase",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_invoices",
        help_text="Optional link to a class purchase.",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total amount to be paid.",
    )

    currency = models.CharField(
        max_length=10,
        blank=True,
        help_text="Currency code for the invoice (e.g., ISO format).",
    )

    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        help_text="Current lifecycle state of the invoice.",
    )

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the invoice was officially issued.",
    )

    due_at = models.DateTimeField(
        help_text="Deadline for payment.",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the invoice was fully paid.",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the invoice was cancelled.",
    )

    expired_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the invoice expired.",
    )

    payment_token = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        help_text="Secure token used for generating payment links.",
    )

    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration timestamp for the payment token.",
    )

    custom_payment_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Optional override link for payment.",
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last invoice email dispatch.",
    )

    email_sent_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the invoice email has been sent.",
    )

    payment_intent_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Reference identifier linking this invoice to a payment intent "
            "in the payments_processor domain."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the invoice was created.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the invoice was last updated.",
    )

    class Meta:
        """
        Model configuration and indexing strategy.

        Indexes are designed to optimize common query patterns such as:
            - tenant-scoped queries
            - status filtering
            - due date queries
            - lookup by reference or token
        """

        ordering = ("-created_at",)

        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "due_at"]),
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["payment_token"]),
            models.Index(fields=["payment_intent_reference"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable string representation of the invoice.

        Returns:
            str: Human-readable invoice identifier.
        """
        return f"Invoice {self.reference}"