from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class OrderReview(models.Model):
    """Client review of a completed order and the assigned writer."""

    ORIGIN_CHOICES = [
        ("client", "Client"),
        ("staff", "Staff"),
    ]

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_reviews",
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="client_review",
    )
    # Cached from order.assigned_writer at review time
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_reviews_received",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_reviews",
    )

    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default="client")

    is_approved = models.BooleanField(default=False, db_index=True)
    is_flagged = models.BooleanField(default=False, db_index=True)
    is_shadowed = models.BooleanField(default=False, db_index=True)

    submitted_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["writer", "is_approved"]),
            models.Index(fields=["website", "submitted_at"]),
        ]

    def __str__(self) -> str:
        return f"Order #{self.order_id} review ({self.rating}★)"
