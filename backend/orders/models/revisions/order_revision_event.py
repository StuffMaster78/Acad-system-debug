from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderRevisionEventType
from websites.models.websites import Website


class OrderRevisionEvent(models.Model):
    """
    Record immutable business events for free revision requests.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_revision_events",
        help_text="Tenant website that owns this revision event.",
    )
    revision_request = models.ForeignKey(
        "orders.OrderRevisionRequest",
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Revision request this event belongs to.",
    )
    event_type = models.CharField(
        max_length=32,
        choices=OrderRevisionEventType.choices,
        help_text="Type of revision business event.",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_revision_events",
        null=True,
        blank=True,
        help_text="Actor associated with the event.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured event metadata.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the event occurred.",
    )

    class Meta:
        """
        Configure ordering and indexes for revision events.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "revision_request"]),
            models.Index(fields=["revision_request", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable revision event description.

        Returns:
            str:
                Human readable event representation.
        """
        request_pk = (
            self.revision_request.pk
            if self.revision_request is not None
            else None
        )
        return f"OrderRevisionEvent request={request_pk}"

    def clean(self) -> None:
        """
        Validate revision event invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.revision_request is not None and self.website is not None:
            if self.website.pk != self.revision_request.website.pk:
                raise ValidationError(
                    "Revision event website must match revision website."
                )