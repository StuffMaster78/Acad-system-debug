from __future__ import annotations

from django.conf import settings
from django.db import models

from websites.models.websites import Website


class UnpaidOrderMessage(models.Model):
    """
    Admin managed message template for unpaid order follow ups.

    Messages are evaluated in ascending sequence order. Each message
    becomes due after `interval_hours` from order creation.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="unpaid_order_messages",
    )
    name = models.CharField(
        max_length=255,
        help_text="Internal admin label for the reminder message.",
    )
    sequence_number = models.PositiveIntegerField(
        help_text="Execution order for this message within a website.",
    )
    interval_hours = models.PositiveIntegerField(
        help_text="Hours after order creation when this message is due.",
    )
    subject = models.CharField(
        max_length=255,
        help_text="Message subject shown in email or in app notification.",
    )
    message = models.TextField(
        help_text="Template body for the unpaid order reminder.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this message is active for scheduling.",
    )
    cancel_order_after_send = models.BooleanField(
        default=False,
        help_text="Cancel the order after successful final send.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_unpaid_order_messages",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_unpaid_order_messages",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("website", "sequence_number", "interval_hours", "id")
        verbose_name = "Unpaid Order Message"
        verbose_name_plural = "Unpaid Order Messages"
        constraints = [
            models.UniqueConstraint(
                fields=("website", "sequence_number"),
                name="uq_unpaid_order_message_website_sequence",
            ),
        ]
        indexes = [
            models.Index(fields=("website", "is_active")),
            models.Index(fields=("website", "sequence_number")),
        ]

    def __str__(self) -> str:
        return f"{self.website.pk} | {self.sequence_number} | {self.name}"