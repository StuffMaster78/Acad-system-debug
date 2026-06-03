"""
User acquisition / campaign attribution.

Created at registration time. Captures the UTM parameters and referrer
from the landing page session so orders can be attributed to channels.

Attribution model: first-touch (captures first visit UTMs before account creation).
"""
from django.conf import settings
from django.db import models


class UserAcquisition(models.Model):
    """
    Campaign and referral attribution for a user's registration session.
    One record per user — created at registration, never overwritten.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="acquisition",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_acquisitions",
    )

    # ── UTM parameters (from the landing URL before registration) ─────────────
    utm_source   = models.CharField(max_length=255, blank=True, default="",
        help_text="e.g. facebook, google, newsletter, organic")
    utm_medium   = models.CharField(max_length=255, blank=True, default="",
        help_text="e.g. cpc, email, social, referral")
    utm_campaign = models.CharField(max_length=255, blank=True, default="",
        help_text="e.g. spring_sale_2026, nursing_essay_fb")
    utm_content  = models.CharField(max_length=255, blank=True, default="",
        help_text="e.g. banner_v2, cta_button_blue")
    utm_term     = models.CharField(max_length=255, blank=True, default="",
        help_text="Paid keyword, e.g. nursing essay help")

    # ── Landing context ────────────────────────────────────────────────────────
    referrer     = models.TextField(blank=True, default="",
        help_text="HTTP Referer header on the first tracked page load.")
    landing_page = models.TextField(blank=True, default="",
        help_text="Full URL (path + query) of the first page the user visited.")

    # ── Derived channel (set at save time) ────────────────────────────────────
    channel = models.CharField(max_length=64, blank=True, default="",
        help_text="Human-readable channel: organic_search, paid_social, email, direct, referral…")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Acquisition"
        indexes = [
            models.Index(fields=["website", "utm_source"]),
            models.Index(fields=["website", "channel"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} | {self.channel or self.utm_source or 'direct'}"

    def save(self, *args, **kwargs):
        if not self.channel:
            self.channel = _derive_channel(
                self.utm_source, self.utm_medium, self.referrer
            )
        super().save(*args, **kwargs)


def _derive_channel(source: str, medium: str, referrer: str) -> str:
    """Best-effort channel classification matching GA4's default channel grouping."""
    s = source.lower().strip()
    m = medium.lower().strip()
    r = referrer.lower()

    if not s and not m:
        if r:
            return "referral"
        return "direct"

    if m in ("cpc", "ppc", "paid", "paidsearch"):
        return "paid_search"
    if m in ("cpv", "paid_video"):
        return "paid_video"
    if m in ("paid_social", "paidsocial") or (s in ("facebook", "instagram", "tiktok", "snapchat", "twitter", "x", "linkedin", "pinterest") and m in ("cpc", "paid", "social")):
        return "paid_social"
    if m in ("email", "newsletter"):
        return "email"
    if m in ("affiliate", "partner"):
        return "affiliate"
    if m in ("sms", "text"):
        return "sms"
    if m == "referral" or (not m and r):
        return "referral"
    if m in ("organic", "") and s in ("google", "bing", "yahoo", "duckduckgo", "baidu"):
        return "organic_search"
    if m == "social" or s in ("facebook", "instagram", "tiktok", "twitter", "x", "linkedin", "youtube", "pinterest"):
        return "organic_social"
    if s == "direct" or (not s and not m):
        return "direct"
    return "other"
