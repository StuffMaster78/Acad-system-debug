from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class WriterReview(models.Model):
    """Client review of a writer. Submitted after order completion."""

    ORIGIN_CHOICES = [
        ("client", "Client"),
        ("staff", "Staff (added on behalf of client)"),
    ]

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="writer_reviews_given",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="writer_reviews_received",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_reviews",
    )

    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(blank=True)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default="client")

    # Moderation flags
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
        return f"{self.reviewer} → {self.writer} ({self.rating}★)"
