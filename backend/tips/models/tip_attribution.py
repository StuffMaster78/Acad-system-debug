from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from tips.enums.tip_context_type import TipContextType


class TipAttribution(models.Model):
    """
    Associates a tip with a domain context.

    A tip may originate from:
    - an order
    - a class purchase
    - a special order
    - a direct writer appreciation event
    - an uncategorized/manual appreciation flow

    This model intentionally separates contextual attribution from
    the core financial tip record.
    """

    tip = models.OneToOneField(
        "tips.Tip",
        on_delete=models.CASCADE,
        related_name="attribution",
    )

    context_type = models.CharField(
        max_length=32,
        choices=TipContextType.choices,
        db_index=True,
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tips",
    )

    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tips",
    )

    class_purchase = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tips",
    )

    reason = models.TextField(
        blank=True,
        help_text=(
            "Optional contextual explanation for the tip."
        ),
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "context_type",
                    "created_at",
                ],
                name="tip_attr_context_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.context_type} attribution "
            f"for Tip {self.tip.pk}"
        )

    def clean(self) -> None:
        """
        Validate attribution consistency.
        """
        super().clean()

        if (
            self.context_type == TipContextType.ORDER
            and self.order is None
        ):
            raise ValidationError(
                {
                    "order": (
                        "Order attribution requires an order."
                    ),
                }
            )

        if (
            self.context_type
            == TipContextType.SPECIAL_ORDER
            and self.special_order is None
        ):
            raise ValidationError(
                {
                    "special_order": (
                        "Special order attribution requires "
                        "a special order."
                    ),
                }
            )

        if (
            self.context_type == TipContextType.CLASS
            and self.class_purchase is None
        ):
            raise ValidationError(
                {
                    "class_purchase": (
                        "Class attribution requires a class "
                        "purchase."
                    ),
                }
            )

        if (
            self.context_type == TipContextType.OTHER
            and not self.reason.strip()
        ):
            raise ValidationError(
                {
                    "reason": (
                        "Other attribution requires a reason."
                    ),
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        Persist attribution safely.
        """
        self.full_clean()

        super().save(*args, **kwargs)
