from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderRevisionStatus
from websites.models.websites import Website


class OrderRevisionRequest(models.Model):
    """
    Represent a free revision request within the free revision window.

    Paid revisions should not be stored here. After the free window, the
    request must be routed into the adjustment workflow.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_revision_requests",
        help_text="Tenant website that owns this revision request.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="revision_requests",
        help_text="Order this revision request belongs to.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_revisions",
        null=True,
        blank=True,
        help_text="Actor who requested the revision.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_revisions",
        null=True,
        blank=True,
        help_text="Actor who reviewed the revision request.",
    )
    status = models.CharField(
        max_length=24,
        choices=OrderRevisionStatus.choices,
        default=OrderRevisionStatus.PENDING,
        help_text="Lifecycle state of the free revision request.",
    )
    instructions = models.TextField(
        help_text="Client revision instructions.",
    )
    client_notes = models.TextField(
        blank=True,
        help_text="Optional client notes for the revision.",
    )
    writer_notes = models.TextField(
        blank=True,
        help_text="Optional writer notes for the revision.",
    )
    is_within_free_window = models.BooleanField(
        default=True,
        help_text="Snapshot of free window eligibility at creation.",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the revision work was re submitted.",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the revision result was accepted.",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the revision request was rejected.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the revision request was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the revision request was last updated.",
    )

    class Meta:
        """
        Configure ordering and indexes for revision requests.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable revision request description.

        Returns:
            str:
                Human readable revision representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return f"OrderRevisionRequest order={order_pk}"

    def clean(self) -> None:
        """
        Validate revision invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Revision website must match order website."
                )