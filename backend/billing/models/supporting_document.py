from __future__ import annotations

from django.db import models

from billing.models.base import BillingBaseModel


class SupportingDocument(BillingBaseModel):
    """
    Store supporting files for billing records.

    Supporting documents may include quotations, approvals, generated
    PDFs, or any other billing-related attachment.
    """

    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
        help_text="Linked invoice for this document, if applicable.",
    )
    payment_request = models.ForeignKey(
        "billing.PaymentRequest",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
        help_text="Linked payment request for this document, if any.",
    )
    file = models.FileField(
        upload_to="billing/documents/",
        help_text="Stored billing document file.",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short display title for the document.",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed note describing the document.",
    )

    class Meta(BillingBaseModel.Meta):
        """
        Configure ordering and index strategy for supporting documents.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable document representation.

        Returns:
            str: Human-readable document description.
        """
        return f"SupportingDocument {self.pk}"