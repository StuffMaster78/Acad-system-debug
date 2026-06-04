from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class WebsiteReview(models.Model):
    """Client review of a writing service website (platform rating)."""

    ORIGIN_CHOICES = [
        ("client", "Client"),
        ("staff", "Staff"),
    ]

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="website_reviews",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="website_reviews",
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
        unique_together = [("reviewer", "website")]
        indexes = [
            models.Index(fields=["website", "is_approved"]),
        ]

    def __str__(self) -> str:
        return f"{self.reviewer} → {self.website} ({self.rating}★)"
