from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class SitePromoDisplay(models.Model):
    """
    A scheduled promotional strip or popup shown on marketing sites.

    Admin/superadmin creates one per website per promotion window.
    Only one record can be active at a time per website (enforced by the
    public API — the most recently started active record wins).

    The frontend counts down to `ends_at` if display_type is countdown_banner.
    """

    STRIP    = "banner_strip"
    COUNTDOWN = "countdown_banner"
    POPUP    = "popup"
    DISPLAY_CHOICES = [
        (STRIP,     "Banner strip"),
        (COUNTDOWN, "Countdown banner"),
        (POPUP,     "Popup"),
    ]

    SCHEME_BRAND = "brand"
    SCHEME_DARK  = "dark"
    SCHEME_WARM  = "warm"
    SCHEME_CHOICES = [
        (SCHEME_BRAND, "Brand (default)"),
        (SCHEME_DARK,  "Dark"),
        (SCHEME_WARM,  "Warm / amber"),
    ]

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="promo_displays",
    )
    campaign = models.ForeignKey(
        "discounts.PromotionalCampaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promo_displays",
        help_text="Optional — links this display to a discount campaign.",
    )

    display_type = models.CharField(max_length=32, choices=DISPLAY_CHOICES, default=STRIP)
    color_scheme = models.CharField(max_length=16, choices=SCHEME_CHOICES, default=SCHEME_BRAND)

    # Content
    badge_text    = models.CharField(max_length=40, blank=True, default="",
                                     help_text='Short label shown before the headline, e.g. "Flash sale" or "Limited time".')
    headline      = models.CharField(max_length=120)
    subtext       = models.CharField(max_length=200, blank=True, default="")
    cta_label     = models.CharField(max_length=60, default="Order now")
    cta_url       = models.CharField(max_length=255, default="/order")
    discount_code = models.CharField(max_length=60, blank=True, default="",
                                     help_text="Discount code shown to visitors (optional).")

    # Schedule — the frontend counts down to ends_at
    starts_at = models.DateTimeField()
    ends_at   = models.DateTimeField()

    is_active = models.BooleanField(default=True,
                                    help_text="Toggle off to hide without deleting.")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="promo_displays_created",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]
        indexes = [
            models.Index(fields=["website", "is_active", "starts_at"]),
            models.Index(fields=["website", "ends_at"]),
        ]
        verbose_name = "Site promo display"
        verbose_name_plural = "Site promo displays"

    def __str__(self) -> str:
        return f"{self.website} — {self.headline} ({self.display_type})"

    @property
    def is_live(self) -> bool:
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at
