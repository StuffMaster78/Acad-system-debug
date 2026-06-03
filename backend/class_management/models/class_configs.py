from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class ClassServiceConfig(models.Model):
    """
    Tenant-scoped client-facing class service configuration.

    The client sees safe labels and choices; internal pricing/payment policy is
    snapshotted onto each class order at creation time for later staff review.
    """

    PRICING_MODE_QUOTE = "quote"
    PRICING_MODE_PACKAGE = "package"
    PRICING_MODE_CHOICES = [
        (PRICING_MODE_QUOTE, "Quote after review"),
        (PRICING_MODE_PACKAGE, "Package estimate"),
    ]

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="class_service_configs",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    service_type = models.CharField(max_length=80, default="full_class")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    pricing_mode = models.CharField(
        max_length=20,
        choices=PRICING_MODE_CHOICES,
        default=PRICING_MODE_QUOTE,
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=10, default="USD")

    duration_options = models.JSONField(default=list, blank=True)
    workload_options = models.JSONField(default=list, blank=True)
    task_options = models.JSONField(default=list, blank=True)
    required_fields = models.JSONField(default=list, blank=True)

    requires_portal_access = models.BooleanField(default=True)
    allow_installments = models.BooleanField(default=True)
    require_deposit_before_start = models.BooleanField(default=True)
    deposit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    quote_expiry_hours = models.PositiveIntegerField(default=72)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_class_service_configs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "slug"],
                name="unique_class_service_config_slug_per_website",
            ),
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_class_service_config_name_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "slug"]),
            models.Index(fields=["display_order"]),
        ]

    def __str__(self) -> str:
        return self.name
