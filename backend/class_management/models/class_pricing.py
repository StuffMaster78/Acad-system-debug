from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from class_management.constants import ClassProposalStatus


class ClassPriceProposal(models.Model):
    """
    Admin proposed class price.

    Multiple proposals can exist over time as negotiation happens.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="price_proposals",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)

    currency = models.CharField(max_length=10, default="USD")

    status = models.CharField(
        max_length=30,
        choices=ClassProposalStatus.choices,
        default=ClassProposalStatus.DRAFT,
        db_index=True,
    )

    message_to_client = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    pricing_snapshot = models.JSONField(default=dict, blank=True)
    discount_snapshot = models.JSONField(default=dict, blank=True)

    expires_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_class_price_proposals",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_class_price_proposals",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["class_order", "status"]),
        ]


class ClassPriceCounterOffer(models.Model):
    """
    Client or staff counter offer during negotiation.
    """

    proposal = models.ForeignKey(
        "class_management.ClassPriceProposal",
        on_delete=models.CASCADE,
        related_name="counter_offers",
    )

    offered_amount = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="class_price_counter_offers",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]