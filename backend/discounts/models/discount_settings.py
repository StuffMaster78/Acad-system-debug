from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class DiscountSettings(models.Model):
    """
    Tenant level discount behavior settings.

    This model controls how discounts behave for a website. It does not
    represent a discount code. Actual discount codes live in Discount.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_settings",
    )

    allow_manual_codes = models.BooleanField(default=True)

    auto_apply_first_order_discount = models.BooleanField(default=True)
    allow_code_to_replace_first_order = models.BooleanField(default=True)
    auto_apply_best_discount = models.BooleanField(default=True)

    allow_discounts_on_orders = models.BooleanField(default=True)
    allow_discounts_on_special_orders = models.BooleanField(default=True)
    allow_discounts_on_class_bundles = models.BooleanField(default=True)

    require_admin_approval_for_campaigns = models.BooleanField(default=False)
    notify_admins_on_large_discount = models.BooleanField(default=True)

    large_discount_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_discount_settings",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_discount_settings",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website"]),
        ]

    def __str__(self) -> str:
        return f"Discount settings for {self.website.id}"