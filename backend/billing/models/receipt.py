from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from billing.constants import ReceiptStatus
from billing.models.base import BillingBaseModel


def generate_receipt_reference() -> str:
    """
    Generate a short human-readable receipt reference.

    Returns:
        str:
            Uppercase alphanumeric reference string.
    """
    return uuid.uuid4().hex[:10].upper()


class Receipt(BillingBaseModel):
    """
    Represent a post-settlement customer-facing receipt.

    A receipt confirms that money was successfully settled for a billing
    object. It is a payment confirmation artifact, not a payment rail,
    receivable, or negotiation object.

    Responsibilities:
        1. Store proof of settlement.
        2. Preserve recipient details.
        3. Preserve tenant branding snapshots.
        4. Link to the billing object that was settled.

    Non-responsibilities:
        1. Payment collection.
        2. Settlement verification.
        3. Reminder logic.
        4. Invoice lifecycle management.
        5. Payment request lifecycle management.

    Design principles:
        1. Dumb model.
        2. Tenant-aware.
        3. Snapshot-oriented for historical stability.
        4. Flexible enough to support multiple billing sources.
    """

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_receipts",
        help_text="Linked user recipient when the recipient exists.",
    )
    recipient_email = models.EmailField(
        blank=True,
        help_text="Fallback recipient email when no client is linked.",
    )
    recipient_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Display name for the receipt recipient.",
    )
    reference = models.CharField(
        max_length=32,
        unique=True,
        default=generate_receipt_reference,
        editable=False,
        help_text="Unique human-readable receipt reference.",
    )

    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        help_text="Invoice settled by this receipt, when applicable.",
    )
    payment_request = models.ForeignKey(
        "billing.PaymentRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        help_text=(
            "Billing payment request settled by this receipt, when "
            "applicable."
        ),
    )

    title_snapshot = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Short title describing what the payment covered at the "
            "time the receipt was issued."
        ),
    )
    description_snapshot = models.TextField(
        blank=True,
        help_text=(
            "Longer human-readable description of what the payment "
            "covered at the time the receipt was issued."
        ),
    )
    company_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Tenant company or brand name shown to the client when the "
            "payment was made."
        ),
    )
    website_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Website display name shown to the client when the payment "
            "was made."
        ),
    )
    website_domain_snapshot = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Website domain or hostname shown to the client when the "
            "payment was made."
        ),
    )
    support_email_snapshot = models.EmailField(
        blank=True,
        help_text=(
            "Support email presented on the receipt at the time of "
            "issuance."
        ),
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Settled amount acknowledged by the receipt.",
    )
    currency = models.CharField(
        max_length=10,
        blank=True,
        help_text="Currency code used for the settled amount.",
    )
    status = models.CharField(
        max_length=20,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.ISSUED,
        help_text="Current lifecycle state of the receipt.",
    )

    payment_intent_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment intent reference tied to the receipt.",
    )
    external_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External payment provider reference.",
    )
    payment_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment provider used for the settled transaction.",
    )

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the receipt was issued.",
    )
    voided_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the receipt was voided.",
    )

    class Meta(BillingBaseModel.Meta):
        """
        Configure ordering and index strategy for receipts.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["website", "client"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["invoice"]),
            models.Index(fields=["payment_request"]),
            models.Index(fields=["payment_intent_reference"]),
            models.Index(fields=["external_reference"]),
            models.Index(fields=["issued_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable receipt representation.

        Returns:
            str:
                Human-readable receipt reference.
        """
        return f"Receipt {self.reference}"