from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


from orders.enums import (
    OrderAssignmentSource,
    OrderAssignmentStatus,
)
from websites.models.websites import Website


class OrderAssignment(models.Model):
    """
    Represent assignment of a writer to an order.

    This model enables:
        1. Assignment history tracking
        2. Reassignment workflows
        3. Future multi-writer support
        4. Audit visibility for ops
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_assignments",
        help_text="Tenant website that owns this assignment.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Order being assigned.",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_assignments",
        help_text="Writer assigned to the order.",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_orders",
        null=True,
        blank=True,
        help_text="Actor who performed the assignment.",
    )
    source = models.CharField(
        max_length=32,
        choices=OrderAssignmentSource.choices,
        help_text="How this assignment came to exist.",
    )
    status = models.CharField(
        max_length=16,
        choices=OrderAssignmentStatus.choices,
        default=OrderAssignmentStatus.ACTIVE,
        help_text="Assignment lifecycle status.",
    )
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the active assignment.",
    )
    source_interest = models.ForeignKey(
        "orders.OrderInterest",
        on_delete=models.SET_NULL,
        related_name="resulting_assignments",
        null=True,
        blank=True,
        help_text="Interest record that produced this assignment.",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the assignment was created.",
    )
    released_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the assignment was released.",
    )
    release_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason the assignment was released.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metadata for assignment context.",
    )

    class Meta:
        """
        Configure ordering and indexes.
        """

        ordering = ("-assigned_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "is_current"]),
            models.Index(fields=["writer", "status"]),
            models.Index(fields=["source", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(is_current=True),
                name="orders_one_current_assignment_per_order",
            ),
        ]

    def __str__(self) -> str:
        """
        Return readable assignment string.
        """
        order_pk = self.order.pk if self.order is not None else None
        writer_pk = self.writer.pk if self.writer is not None else None
        return f"OrderAssignment order={order_pk} writer={writer_pk}"

    def clean(self) -> None:
        """
        Validate assignment invariants.

        Raises:
            ValidationError:
                Raised when related objects cross tenants.
        """
        if self.order and self.website:
            if self.order.website.pk != self.website.pk:
                raise ValidationError(
                    "Assignment website must match order website."
                )

        if self.writer and self.website:
            writer_website_id = getattr(
                self.writer,
                "website_id",
                None,
            )
            if writer_website_id and writer_website_id != self.website.pk:
                raise ValidationError(
                    "Writer website must match assignment website."
                )
            
            if self.source_interest is not None:
                if self.order is None:
                    raise ValidationError(
                        "Source interest requires an order."
                    )

                if self.source_interest.order is None:
                    raise ValidationError(
                        "Source interest must belong to an order."
                    )

                if self.source_interest.order.pk != self.order.pk:
                    raise ValidationError(
                        "Source interest must belong to the same order."
                    )