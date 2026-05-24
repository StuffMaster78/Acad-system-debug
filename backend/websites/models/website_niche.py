from __future__ import annotations

from django.db import models


class WebsiteNiche(models.Model):
    """
    Niche and market positioning configuration for a website.
    """

    NICHE_GENERAL = "general_academic"
    NICHE_NURSING = "nursing"
    NICHE_MEDICAL = "medical"
    NICHE_BUSINESS = "business"
    NICHE_STEM = "stem"

    NICHE_CHOICES = [
        (NICHE_GENERAL, "General Academic"),
        (NICHE_NURSING, "Nursing"),
        (NICHE_MEDICAL, "Medical"),
        (NICHE_BUSINESS, "Business"),
        (NICHE_STEM, "STEM"),
    ]

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="niche",
    )

    niche_type = models.CharField(
        max_length=64,
        choices=NICHE_CHOICES,
        default=NICHE_GENERAL,
    )

    service_catalog = models.JSONField(default=list, blank=True)
    subject_catalog = models.JSONField(default=list, blank=True)
    order_form_defaults = models.JSONField(default=dict, blank=True)
    seo_defaults = models.JSONField(default=dict, blank=True)

    writer_pool_rules = models.JSONField(default=dict, blank=True)
    pricing_defaults = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Niche"
        verbose_name_plural = "Website Niches"

    def __str__(self) -> str:
        return f"{self.website} niche config"