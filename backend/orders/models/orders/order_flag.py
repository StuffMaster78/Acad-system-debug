from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderFlag(models.Model):
    """
    Represent an operational or commercial flag attached to an order.

    Flags are not order lifecycle statuses.
    They are supplemental classifications used by staff dashboards,
    staffing rules, urgency handling, and monitoring.

    Examples:
        hvo:
            High value order.
        uo:
            Urgent order.
        hot:
            Extremely urgent order.
        po:
            Preferred writer order.
        rco:
            Returning client order snapshot flag.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_flags",
        help_text="Tenant website that owns this order flag.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="flags",
        help_text="Order this flag belongs to.",
    )
    flag_key = models.CharField(
        max_length=32,
        help_text="Machine readable flag key such as hvo or hot.",
    )
    source = models.CharField(
        max_length=32,
        default="system",
        help_text="Origin of the flag such as system or staff.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this flag is currently active.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metadata describing why the flag exists.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the flag record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the flag record was last updated.",
    )

    class Meta:
        """
        Configure ordering and uniqueness for order flags.
        """

        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["order", "flag_key"],
                name="unique_order_flag_key",
            )
        ]
        indexes = [
            models.Index(fields=["website", "flag_key"]),
            models.Index(fields=["order", "is_active"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable flag representation.

        Returns:
            str:
                Human readable order flag string.
        """
        order_pk = (
            self.order.pk
            if getattr(self, "order", None) is not None
            else None
        )
        return (
            f"OrderFlag(order={order_pk}, "
            f"flag_key={self.flag_key}, active={self.is_active})"
        )

    def clean(self) -> None:
        """
        Validate tenant consistency.

        Raises:
            ValidationError:
                Raised when order and website tenants do not match.
        """
        super().clean()

        order = getattr(self, "order", None)
        website = getattr(self, "website", None)

        if order is None or website is None:
            return

        order_website = getattr(order, "website", None)
        order_website_pk = (
            order_website.pk if order_website is not None else None
        )
        website_pk = getattr(website, "pk", None)

        if website_pk != order_website_pk:
            raise ValidationError(
                "Order flag website must match order website."
            )