from __future__ import annotations

from django.conf import settings
from django.db import models


class ChangelogEntry(models.Model):
    """
    A release note entry visible to one or more portal surfaces.

    Superadmins and admins create entries via the Django admin.
    Each entry is scoped to a website and targeted at specific portals
    (client, writer, staff, or public — the website homepage).
    """

    SURFACE_CHOICES = [
        ("client", "Client portal"),
        ("writer", "Writer portal"),
        ("staff", "Staff portal"),
        ("public", "Public (all)"),
    ]

    TYPE_CHOICES = [
        ("feature", "New feature"),
        ("improvement", "Improvement"),
        ("fix", "Bug fix"),
        ("maintenance", "Maintenance"),
        ("notice", "Notice"),
    ]

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="changelog_entries",
        help_text="Leave blank to show on all websites.",
        null=True,
        blank=True,
    )
    portal_surface = models.CharField(
        max_length=20,
        choices=SURFACE_CHOICES,
        default="public",
        db_index=True,
    )
    entry_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="feature",
    )
    version = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional — e.g. '2026-06-04' or '1.4.2'",
    )
    title = models.CharField(max_length=255)
    body = models.TextField(help_text="Markdown supported.")
    is_published = models.BooleanField(default=False, db_index=True)
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned entries appear at the top regardless of date.",
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="changelog_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["portal_surface", "is_published", "-published_at"]),
            models.Index(fields=["website", "portal_surface", "is_published"]),
        ]

    def __str__(self) -> str:
        return f"[{self.portal_surface}] {self.title}"
