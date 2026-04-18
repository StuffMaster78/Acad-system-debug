from __future__ import annotations

from django.conf import settings
from django.db import models

from orders.constants import (
    UnpaidOrderDispatchStatus,
)
from websites.models.websites import Website


class UnpaidOrderMessageDispatch(models.Model):
    """
    Delivery log for unpaid order reminders.

    A dispatch is created when a rule becomes due for an eligible order.
    Sent and failed records are preserved for audit and support review.
    Pending dispatches may be cancelled when the order becomes
    ineligible.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="unpaid_order_message_dispatches",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="unpaid_order_message_dispatches",
    )
    unpaid_order_message = models.ForeignKey(
        "orders.UnpaidOrderMessage",
        on_delete=models.CASCADE,
        related_name="dispatches",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="unpaid_order_message_dispatches",
    )
    recipient_email = models.EmailField()
    subject_snapshot = models.CharField(max_length=255)
    message_snapshot = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=UnpaidOrderDispatchStatus.choices,
        default=UnpaidOrderDispatchStatus.PENDING,
    )
    scheduled_for = models.DateTimeField()
    attempted_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("scheduled_for", "id")
        verbose_name = "Unpaid Order Message Dispatch"
        verbose_name_plural = "Unpaid Order Message Dispatches"
        constraints = [
            models.UniqueConstraint(
                fields=("order", "unpaid_order_message"),
                name="uq_unpaid_order_dispatch_order_message",
            ),
        ]
        indexes = [
            models.Index(fields=("website", "status", "scheduled_for")),
            models.Index(fields=("order", "status")),
            models.Index(fields=("client", "status")),
        ]

    def __str__(self) -> str:
        return (
            f"{self.order.pk} | {self.unpaid_order_message.pk} | "
            f"{self.status}"
        )