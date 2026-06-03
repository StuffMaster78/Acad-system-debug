from __future__ import annotations

from django.conf import settings
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
    payment_client_disclosure_text = models.TextField(
        blank=True,
        help_text="Optional custom disclosure text shown to clients before payment.",
    )
    payment_support_contact = models.CharField(
        max_length=120,
        blank=True,
        help_text="Billing support contact shown beside payment disclosure.",
    )
    payment_requires_acknowledgement = models.BooleanField(
        default=True,
        help_text="Require authenticated clients to acknowledge the disclosure before payment.",
    )

    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Branding"
        verbose_name_plural = "Website Branding"

    def __str__(self) -> str:
        return self.brand_name


class PaymentDisclosureAcknowledgement(models.Model):
    """
    Audit trail proving a client saw and/or acknowledged payment disclosure.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="payment_disclosure_acknowledgements",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_disclosure_acknowledgements",
    )
    processor_display_name = models.CharField(max_length=120, blank=True)
    statement_descriptor = models.CharField(max_length=22, blank=True)
    client_disclosure_text = models.TextField(blank=True)
    support_contact = models.CharField(max_length=120, blank=True)
    context = models.CharField(max_length=80, blank=True)
    reference_type = models.CharField(max_length=80, blank=True)
    reference_id = models.CharField(max_length=80, blank=True)
    shown_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "user", "context"], name="websites_pa_website_dd10e2_idx"),
            models.Index(fields=["website", "reference_type", "reference_id"], name="websites_pa_website_278423_idx"),
            models.Index(fields=["shown_at"], name="websites_pa_shown_a_3e6f1e_idx"),
            models.Index(fields=["acknowledged_at"], name="websites_pa_acknowl_a074e2_idx"),
        ]

    def __str__(self) -> str:
        state = "acknowledged" if self.acknowledged_at else "shown"
        return f"{self.website} payment disclosure {state}"
