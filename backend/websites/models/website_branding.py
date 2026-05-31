from __future__ import annotations

from django.db import models


class WebsiteBranding(models.Model):
    """
    Public-facing brand settings for a tenant website.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="public_branding",
    )

    brand_name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=255, blank=True)

    logo_url = models.URLField(blank=True)
    favicon_url = models.URLField(blank=True)

    primary_color = models.CharField(max_length=24, default="#2563eb")
    secondary_color = models.CharField(max_length=24, default="#0f172a")
    accent_color = models.CharField(max_length=24, default="#14b8a6")

    homepage_headline = models.CharField(max_length=255, blank=True)
    homepage_subheadline = models.TextField(blank=True)

    trust_claims = models.JSONField(default=list, blank=True)
    footer_disclaimer = models.TextField(blank=True)

    payment_processor_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Display name of the payment processor shown to clients, e.g. 'OrderBridge Payments'",
    )
    payment_statement_descriptor = models.CharField(
        max_length=22,
        blank=True,
        help_text="Exact string clients will see on their card statement, e.g. 'ORDERBRIDGE PAYMENTS'",
    )

    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Branding"
        verbose_name_plural = "Website Branding"

    def __str__(self) -> str:
        return self.brand_name