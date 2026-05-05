from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class PromotionalCampaign(models.Model):
    """
    Marketing campaign that groups related discounts.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_campaigns",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)

    description = models.TextField(blank=True)

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_discount_campaigns",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_discount_campaigns",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = (("website", "slug"),)
        indexes = [
            models.Index(fields=["website", "slug"]),
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "is_archived"]),
        ]

    def __str__(self) -> str:
        return self.name