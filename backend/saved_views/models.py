from __future__ import annotations

from django.conf import settings
from django.db import models


class SavedView(models.Model):
    """
    A named filter preset saved by a staff user for a specific admin view.
    Stored per-user so each staff member has their own saved presets.
    """

    VIEW_TYPE_CHOICES = [
        ("orders", "Order list"),
        ("clients", "Client list"),
        ("writers", "Writer list"),
        ("payments", "Payments"),
        ("disputes", "Disputes"),
        ("analytics", "Analytics"),
        ("feedback", "Feedback triage"),
        ("audit", "Audit log"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_views",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="saved_views",
        null=True,
        blank=True,
    )
    view_type = models.CharField(max_length=30, choices=VIEW_TYPE_CHOICES, db_index=True)
    name = models.CharField(max_length=100)
    filters = models.JSONField(
        default=dict,
        help_text="Serialised filter state — keys/values vary by view_type.",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Load this preset automatically when opening the view.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]
        unique_together = [("user", "view_type", "name")]
        indexes = [
            models.Index(fields=["user", "view_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} — {self.view_type}/{self.name}"
