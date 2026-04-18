from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderScope(models.Model):
    """
    Store the base scope of an order.

    This record represents the originally purchased or directly edited
    base scope. Paid incremental changes should flow through funded
    adjustment records rather than directly mutating the order root.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_scopes",
        help_text="Tenant website that owns this scope record.",
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="scope",
        help_text="Order this scope record belongs to.",
    )
    number_of_pages = models.PositiveIntegerField(
        default=1,
        help_text="Base number of pages in the order.",
    )
    number_of_slides = models.PositiveIntegerField(
        default=0,
        help_text="Base number of slides in the order.",
    )
    number_of_references = models.PositiveIntegerField(
        default=0,
        help_text="Base number of references in the order.",
    )
    spacing = models.CharField(
        max_length=16,
        help_text="Spacing setting for the order.",
    )
    extra_service_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of extra service ids on the base order.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the scope record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the scope record was last updated.",
    )

    class Meta:
        """
        Configure indexes for order scope.
        """

        indexes = [
            models.Index(fields=["website", "order"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable scope description.

        Returns:
            str:
                Human readable scope representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return f"OrderScope order={order_pk}"

    def clean(self) -> None:
        """
        Validate scope invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Scope website must match order website."
                )