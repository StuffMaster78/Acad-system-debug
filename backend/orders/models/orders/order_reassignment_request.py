from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderReassignmentRequesterRole(models.TextChoices):
    """
    Represent the role of the actor requesting reassignment.
    """

    CLIENT = "client", "Client"
    WRITER = "writer", "Writer"
    STAFF = "staff", "Staff"


class OrderReassignmentRequestStatus(models.TextChoices):
    """
    Represent the lifecycle state of a reassignment request.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class OrderReassignmentDecision(models.TextChoices):
    """
    Represent the staff decision for a reassignment request.
    """

    RETURN_TO_POOL = "return_to_pool", "Return To Pool"
    ASSIGN_SPECIFIC_WRITER = (
        "assign_specific_writer",
        "Assign Specific Writer",
    )


class OrderReassignmentRequest(models.Model):
    """
    Represent a request to move an order away from the current writer.

    Either the writer or the client can request reassignment. Staff then
    reviews the request and decides whether to return the order to the
    pool or assign it directly to another writer.

    This model captures the request and review workflow only. It does not
    perform the reassignment itself.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_reassignment_requests",
        help_text="Tenant website that owns this reassignment request.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="reassignment_requests",
        help_text="Order affected by the reassignment request.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_order_reassignments",
        null=True,
        blank=True,
        help_text="Actor who requested reassignment.",
    )
    requester_role = models.CharField(
        max_length=16,
        choices=OrderReassignmentRequesterRole.choices,
        help_text="Role of the actor who requested reassignment.",
    )
    current_assignment = models.ForeignKey(
        "orders.OrderAssignment",
        on_delete=models.SET_NULL,
        related_name="reassignment_requests",
        null=True,
        blank=True,
        help_text="Current assignment being challenged or released.",
    )
    status = models.CharField(
        max_length=16,
        choices=OrderReassignmentRequestStatus.choices,
        default=OrderReassignmentRequestStatus.PENDING,
        help_text="Lifecycle state of the reassignment request.",
    )
    reason = models.TextField(
        help_text="Reason provided for reassignment.",
    )
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes for reassignment review.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_order_reassignments",
        null=True,
        blank=True,
        help_text="Staff actor who reviewed the reassignment request.",
    )
    decision = models.CharField(
        max_length=32,
        choices=OrderReassignmentDecision.choices,
        blank=True,
        help_text="Decision taken after staff review.",
    )
    assign_to_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="targeted_order_reassignments",
        null=True,
        blank=True,
        help_text="Writer chosen when assigning directly.",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the reassignment request was reviewed.",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the reassignment request was cancelled.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metadata for the reassignment workflow.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the reassignment request was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the reassignment request was last updated.",
    )

    class Meta:
        """
        Configure ordering, indexes, and uniqueness for reassignment
        requests.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["requested_by", "status"]),
            models.Index(fields=["reviewed_by", "status"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(
                    status=OrderReassignmentRequestStatus.PENDING
                ),
                name="orders_one_pending_reassignment_per_order",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable reassignment request description.

        Returns:
            str:
                Human readable reassignment request representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return (
            f"OrderReassignmentRequest order={order_pk} "
            f"status={self.status}"
        )

    def clean(self) -> None:
        """
        Validate reassignment request invariants.

        Raises:
            ValidationError:
                Raised when linked objects cross tenants or decision
                fields are inconsistent.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Reassignment website must match order website."
                )

        if self.requested_by is not None and self.website is not None:
            requested_by_website_id = getattr(
                self.requested_by,
                "website_id",
                None,
            )
            if (
                requested_by_website_id is not None
                and requested_by_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Requester website must match reassignment website."
                )

        if self.reviewed_by is not None and self.website is not None:
            reviewed_by_website_id = getattr(
                self.reviewed_by,
                "website_id",
                None,
            )
            if (
                reviewed_by_website_id is not None
                and reviewed_by_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Reviewer website must match reassignment website."
                )

        if self.assign_to_writer is not None and self.website is not None:
            assign_to_writer_website_id = getattr(
                self.assign_to_writer,
                "website_id",
                None,
            )
            if (
                assign_to_writer_website_id is not None
                and assign_to_writer_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Target writer website must match reassignment "
                    "website."
                )

        if self.current_assignment is not None:
            if self.order is None:
                raise ValidationError(
                    "Current assignment requires an order."
                )

            if self.current_assignment.order is None:
                raise ValidationError(
                    "Current assignment must belong to an order."
                )

            if self.current_assignment.order.pk != self.order.pk:
                raise ValidationError(
                    "Current assignment must belong to the same order."
                )

        if self.decision == (
            OrderReassignmentDecision.ASSIGN_SPECIFIC_WRITER
        ):
            if self.assign_to_writer is None:
                raise ValidationError(
                    "assign_to_writer is required when assigning "
                    "a specific writer."
                )

        if self.status == OrderReassignmentRequestStatus.APPROVED:
            if not self.decision:
                raise ValidationError(
                    "decision is required when approving "
                    "a reassignment request."
                )