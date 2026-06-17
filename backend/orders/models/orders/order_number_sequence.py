from __future__ import annotations

from django.db import models


class OrderNumberScope(models.TextChoices):
    NORMAL_ORDER = "normal_order", "Normal Order"
    CLASS_ORDER = "class_order", "Class Order"
    SPECIAL_ORDER = "special_order", "Special Order"


class OrderNumberSequence(models.Model):
    """
    Configurable per-website, per-period order number sequence.

    Lets admin/superadmin set the starting seed for each billing period
    (month, quarter, custom) without touching database primary keys.
    All external-facing order numbers are derived from here; the internal
    Order.id stays as a boring sequential PK and is never shown to clients.

    Example
    -------
    website=1, scope=normal_order, period="2026-07", seed=85673, padding=7
    → order number format: 8567300001, 8567300002, …

    seed is the human-chosen base offset.
    The display reference is: str(seed + order.id), optionally with prefix.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_number_sequences",
    )
    scope = models.CharField(
        max_length=32,
        choices=OrderNumberScope.choices,
        default=OrderNumberScope.NORMAL_ORDER,
    )
    period = models.CharField(
        max_length=20,
        help_text="e.g. '2026-07' or 'Q3-2026'. Admin-defined; not validated by the platform.",
    )
    prefix = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Optional string prefix e.g. 'GC-'. Combined: GC-8567300001",
    )
    seed = models.PositiveBigIntegerField(
        help_text="Admin-chosen leading digits. e.g. 85673 → numbers start 8567300001.",
    )
    padding = models.PositiveSmallIntegerField(
        default=5,
        help_text="Zero-padding width for the auto-increment portion. 5 → 00001..99999.",
    )
    next_number = models.PositiveBigIntegerField(
        default=1,
        help_text="Next auto-increment value. Incremented atomically on each allocation.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive sequences are skipped during allocation.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_number_sequences_created",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order Number Sequence"
        verbose_name_plural = "Order Number Sequences"
        constraints = [
            models.UniqueConstraint(
                fields=["website", "scope", "period"],
                condition=models.Q(is_active=True),
                name="uniq_active_order_number_sequence_per_period",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.website_id} / {self.scope} / {self.period} (seed={self.seed})"

    def format_number(self, n: int) -> str:
        """Return the display order number for internal object id n."""
        return f"{self.prefix}{self.seed + n}"
