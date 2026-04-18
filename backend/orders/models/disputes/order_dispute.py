from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderDisputeStatus(models.TextChoices):
    """
    Represent the lifecycle states of an order dispute.
    """

    OPEN = "open", "Open"
    IN_REVIEW = "in_review", "In Review"
    ESCALATED = "escalated", "Escalated"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"
    CANCELLED = "cancelled", "Cancelled"


class OrderDisputeReason(models.TextChoices):
    """
    Represent common reasons for opening a dispute.
    """

    QUALITY_ISSUE = "quality_issue", "Quality Issue"
    MISSED_INSTRUCTIONS = (
        "missed_instructions",
        "Missed Instructions",
    )
    LATE_DELIVERY = "late_delivery", "Late Delivery"
    WRONG_FILE = "wrong_file", "Wrong File"
    CONDUCT_ISSUE = "conduct_issue", "Conduct Issue"
    PAYMENT_ISSUE = "payment_issue", "Payment Issue"
    OTHER = "other", "Other"


class OrderDispute(models.Model):
    """
    Represent a dispute raised against an order.

    This model stores the dispute root record only. Resolution details and
    dispute timeline are kept in related models.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_disputes",
        help_text="Tenant website that owns this dispute.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="disputes",
        help_text="Order this dispute belongs to.",
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="opened_order_disputes",
        null=True,
        blank=True,
        help_text="Actor who opened the dispute.",
    )
    assigned_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_order_disputes",
        null=True,
        blank=True,
        help_text="Staff actor currently reviewing the dispute.",
    )
    status = models.CharField(
        max_length=24,
        choices=OrderDisputeStatus,
        default=OrderDisputeStatus.OPEN,
        help_text="Current lifecycle state of the dispute.",
    )
    reason = models.CharField(
        max_length=32,
        choices=OrderDisputeReason,
        default=OrderDisputeReason.OTHER,
        help_text="Primary reason for the dispute.",
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title summarizing the dispute.",
    )
    description = models.TextField(
        help_text="Detailed description of the dispute.",
    )
    client_notes = models.TextField(
        blank=True,
        help_text="Optional client notes for the dispute.",
    )
    writer_notes = models.TextField(
        blank=True,
        help_text="Optional writer notes for the dispute.",
    )
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes for dispute handling.",
    )
    opened_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dispute was opened.",
    )
    escalated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dispute was escalated.",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dispute was resolved.",
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dispute was closed.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the record was last updated.",
    )

    class Meta:
        """
        Configure ordering, indexes, and constraints for disputes.
        """

        ordering = ("-opened_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["opened_by", "status"]),
            models.Index(fields=["assigned_reviewer", "status"]),
            models.Index(fields=["opened_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(
                    status__in=[
                        OrderDisputeStatus.OPEN,
                        OrderDisputeStatus.IN_REVIEW,
                        OrderDisputeStatus.ESCALATED,
                    ]
                ),
                name="orders_one_active_dispute_per_order",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable dispute description.

        Returns:
            str:
                Human readable dispute representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return f"OrderDispute order={order_pk} status={self.status}"

    def clean(self) -> None:
        """
        Validate dispute invariants.

        Raises:
            ValidationError:
                Raised when linked objects cross tenants.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Dispute website must match order website."
                )

        if self.opened_by is not None and self.website is not None:
            opened_by_website_id = getattr(
                self.opened_by,
                "website_id",
                None,
            )
            if (
                opened_by_website_id is not None
                and opened_by_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Dispute opener website must match dispute website."
                )

        if self.assigned_reviewer is not None and self.website is not None:
            reviewer_website_id = getattr(
                self.assigned_reviewer,
                "website_id",
                None,
            )
            if (
                reviewer_website_id is not None
                and reviewer_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Reviewer website must match dispute website."
                )