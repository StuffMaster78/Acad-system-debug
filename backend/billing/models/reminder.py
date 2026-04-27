from __future__ import annotations

from django.db import models

from billing.constants import ReminderStatus
from billing.models.base import BillingBaseModel


class Reminder(BillingBaseModel):
    """
    Track reminder attempts for invoices and payment requests.

    This model stores reminder history and outcome. It does not contain
    reminder scheduling logic.
    """

    invoice = models.ForeignKey(
        "billing.Invoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reminders",
        help_text="Linked invoice reminder target, if applicable.",
    )
    payment_request = models.ForeignKey(
        "billing.PaymentRequest",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reminders",
        help_text="Linked payment request reminder target, if any.",
    )
    channel = models.CharField(
        max_length=50,
        help_text="Delivery channel used for the reminder.",
    )
    event_key = models.CharField(
        max_length=100,
        help_text="Notification event key used for dispatch.",
    )
    status = models.CharField(
        max_length=20,
        choices=ReminderStatus.choices,
        default=ReminderStatus.PENDING,
        help_text="Outcome state of the reminder attempt.",
    )
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Scheduled dispatch timestamp for the reminder.",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the reminder was sent.",
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the reminder failed.",
    )
    error_message = models.TextField(
        blank=True,
        help_text="Failure detail when the reminder attempt failed.",
    )

    class Meta(BillingBaseModel.Meta):
        """
        Configure ordering and index strategy for reminders.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "scheduled_for"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable reminder representation.

        Returns:
            str: Human-readable reminder description.
        """
        invoice = self.invoice
        if invoice is not None:
            return f"Reminder for invoice {invoice.reference}"
        
        payment_request = self.payment_request
        if payment_request is not None:
            return (
                "Reminder for payment request "
                f"{payment_request.reference}"
            )
        return f"Reminder {self.pk}"