"""
Quote models for the order_pricing_core app.

These models store progressive quote sessions, evolving quote input,
and internal pricing breakdown lines.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models

from order_pricing_core.constants import BreakdownLineType
from order_pricing_core.constants import QuoteStatus


class PricingQuote(models.Model):
    """
    Stores a progressive pricing quote session.
    """

    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_pricing_quotes",
    )
    service = models.ForeignKey(
        "order_pricing_core.ServiceCatalogItem",
        on_delete=models.PROTECT,
        related_name="pricing_quotes",
    )
    status = models.CharField(
        max_length=20,
        choices=QuoteStatus.CHOICES,
        default=QuoteStatus.DRAFT,
    )
    current_step = models.PositiveSmallIntegerField(default=1)
    estimated_min_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    estimated_max_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    calculated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=10, default="USD")
    is_final = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    converted_object_type = models.CharField(max_length=100, blank=True)
    converted_object_id = models.CharField(max_length=64, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_order_pricing_quotes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_pricing_quote"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Quote {self.session_id}"


class PricingQuoteInput(models.Model):
    """
    Stores evolving quote input fields for a quote session.
    """

    quote = models.OneToOneField(
        PricingQuote,
        on_delete=models.CASCADE,
        related_name="input_data",
    )

    service_code = models.CharField(max_length=100, blank=True)

    paper_type_code = models.CharField(max_length=50, blank=True)
    work_type_code = models.CharField(max_length=50, blank=True)
    subject_code = models.CharField(max_length=50, blank=True)
    academic_level_code = models.CharField(max_length=50, blank=True)
    analysis_level = models.CharField(max_length=20, blank=True)
    spacing = models.CharField(max_length=20, blank=True)

    pages = models.PositiveIntegerField(null=True, blank=True)
    slides = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    deadline_hours = models.PositiveIntegerField(null=True, blank=True)

    diagram_type = models.CharField(max_length=30, blank=True)
    diagram_complexity = models.CharField(max_length=20, blank=True)

    writer_level_code = models.CharField(max_length=50, blank=True)
    preferred_writer_id = models.CharField(max_length=64, blank=True)

    selected_addon_codes = models.JSONField(default=list, blank=True)

    topic = models.CharField(max_length=255, blank=True)
    instructions = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_pricing_quote_input"

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Input for {self.quote.pk}"
    
class PricingQuoteLine(models.Model):
    """
    Stores internal quote breakdown lines.
    """

    quote = models.ForeignKey(
        PricingQuote,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    line_type = models.CharField(
        max_length=20,
        choices=BreakdownLineType.CHOICES,
    )
    code = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    metadata = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_pricing_quote_line"
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.label} | {self.amount}"