from __future__ import annotations

from django.db import models


class WebsiteCookieConfig(models.Model):
    """
    Per-tenant cookie banner configuration.

    Each website can independently control consent/policy version strings,
    the URLs for its privacy and cookie policy pages, and whether marketing
    consent is surfaced to visitors. The CookieConfigView falls back to
    sensible defaults when no row exists for the resolved website.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="cookie_config",
    )

    # Version strings — bumping triggers a fresh consent prompt on the frontend.
    # Format is free-form; ISO date strings (e.g. "2026-06-15") work well.
    consent_version = models.CharField(
        max_length=50,
        default="2026-06-15",
        help_text="Bumping this value forces all visitors to re-consent.",
    )
    policy_version = models.CharField(
        max_length=50,
        default="2026-06-15",
        help_text=(
            "Version of the privacy/cookie policy document. "
            "Should be updated whenever policy content changes."
        ),
    )

    # Per-site policy URLs — defaults to the platform-wide /privacy paths.
    privacy_policy_url = models.CharField(
        max_length=255,
        default="/privacy",
        help_text="Relative or absolute URL for the privacy policy page.",
    )
    cookie_policy_url = models.CharField(
        max_length=255,
        default="/privacy#cookies",
        help_text="Relative or absolute URL for the cookie policy section.",
    )

    # Feature flags
    marketing_available = models.BooleanField(
        default=False,
        help_text=(
            "Show the Marketing consent category. Enable only when the site "
            "has advertising or attribution integrations configured."
        ),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cookie Config"
        verbose_name_plural = "Cookie Configs"

    def __str__(self) -> str:
        return f"CookieConfig for {self.website}"
