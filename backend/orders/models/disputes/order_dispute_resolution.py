from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderDisputeResolutionOutcome(models.TextChoices):
    """
    Represent supported dispute resolution outcomes.
    """

    WRITER_WINS = "writer_wins", "Writer Wins"
    CLIENT_WINS = "client_wins", "Client Wins"
    EXTEND_DEADLINE = "extend_deadline", "Extend Deadline"
    REASSIGN = "reassign", "Reassign"
    PARTIAL_COMPROMISE = "partial_compromise", "Partial Compromise"
    REFUND = "refund", "Refund"
    OTHER = "other", "Other"


class OrderDisputeResolution(models.Model):
    """
    Store the structured resolution details for a dispute.

    One dispute should have at most one final resolution record.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_dispute_resolutions",
        help_text="Tenant website that owns this resolution record.",
    )
    dispute = models.OneToOneField(
        "orders.OrderDispute",
        on_delete=models.CASCADE,
        related_name="resolution",
        help_text="Dispute this resolution belongs to.",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_order_disputes",
        null=True,
        blank=True,
        help_text="Staff actor who resolved the dispute.",
    )
    outcome = models.CharField(
        max_length=32,
        choices=OrderDisputeResolutionOutcome,
        help_text="Structured outcome of the dispute.",
    )
    summary = models.CharField(
        max_length=255,
        help_text="Short summary of the dispute resolution.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Detailed internal notes for the resolution.",
    )
    extend_deadline_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text="New deadline when outcome extends the deadline.",
    )
    reassign_to_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="dispute_reassignments_received",
        null=True,
        blank=True,
        help_text="Replacement writer when outcome is reassignment.",
    )
    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Refund amount decided by the resolution, if any.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured resolution metadata payload.",
    )
    resolved_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the resolution was recorded.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the resolution was last updated.",
    )

    class Meta:
        """
        Configure indexes and constraints for dispute resolutions.
        """

        indexes = [
            models.Index(fields=["website", "outcome"]),
            models.Index(fields=["resolved_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(refund_amount__isnull=True)
                    | models.Q(refund_amount__gte=0)
                ),
                name="orders_dispute_resolution_refund_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable resolution description.

        Returns:
            str:
                Human readable resolution representation.
        """
        dispute_pk = self.dispute.pk if self.dispute is not None else None
        return f"OrderDisputeResolution dispute={dispute_pk}"

    def clean(self) -> None:
        """
        Validate resolution invariants.

        Raises:
            ValidationError:
                Raised when linked objects cross tenants or outcome
                fields are inconsistent.
        """
        if self.dispute is not None and self.website is not None:
            if self.website.pk != self.dispute.website.pk:
                raise ValidationError(
                    "Resolution website must match dispute website."
                )

        if self.resolved_by is not None and self.website is not None:
            resolved_by_website_id = getattr(
                self.resolved_by,
                "website_id",
                None,
            )
            if (
                resolved_by_website_id is not None
                and resolved_by_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Resolver website must match dispute website."
                )

        if self.reassign_to_writer is not None and self.website is not None:
            writer_website_id = getattr(
                self.reassign_to_writer,
                "website_id",
                None,
            )
            if (
                writer_website_id is not None
                and writer_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Reassigned writer website must match dispute "
                    "website."
                )

        if self.outcome == OrderDisputeResolutionOutcome.EXTEND_DEADLINE:
            if self.extend_deadline_to is None:
                raise ValidationError(
                    "extend_deadline_to is required for extend_deadline."
                )

        if self.outcome == OrderDisputeResolutionOutcome.REASSIGN:
            if self.reassign_to_writer is None:
                raise ValidationError(
                    "reassign_to_writer is required for reassign."
                )