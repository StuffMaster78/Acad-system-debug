from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderAdjustmentScopeSnapshot(models.Model):
    """
    Persist before and after scope details for an adjustment.

    This snapshot is useful for audit, support, and dispute handling.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_scope_snapshots",
        help_text="Tenant website that owns this scope snapshot.",
    )
    adjustment_request = models.OneToOneField(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="scope_snapshot",
        help_text="Adjustment request this scope snapshot belongs to.",
    )
    base_scope_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Base order scope before the adjustment.",
    )
    requested_scope_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Requested scope delta payload.",
    )
    authorized_scope_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Authorized scope after funding, if funded.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the scope snapshot was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the scope snapshot was last updated.",
    )

    class Meta:
        """
        Configure indexes for scope snapshots.
        """

        indexes = [
            models.Index(fields=["website", "adjustment_request"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable scope snapshot description.

        Returns:
            str:
                Human readable snapshot representation.
        """
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderAdjustmentScopeSnapshot "
            f"request={request_pk}"
        )

    def clean(self) -> None:
        """
        Validate scope snapshot invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if (
            self.adjustment_request is not None
            and self.website is not None
            and self.website.pk != self.adjustment_request.website.pk
        ):
            raise ValidationError(
                "Scope snapshot website must match adjustment website."
            )