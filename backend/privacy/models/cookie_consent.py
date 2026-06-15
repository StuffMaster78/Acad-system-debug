from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class CookieConsentRecord(models.Model):
    """
    Historical consent record for cookie and device-storage preferences.

    Necessary cookies are always allowed because they are required for security,
    authentication, checkout, and consent preference storage. Optional categories
    are recorded explicitly so the frontend can gate analytics/marketing scripts.
    """

    SOURCE_BANNER = "banner"
    SOURCE_SETTINGS = "settings"
    SOURCE_FOOTER = "footer"
    SOURCE_API = "api"

    SOURCE_CHOICES = [
        (SOURCE_BANNER, "Cookie banner"),
        (SOURCE_SETTINGS, "Cookie settings"),
        (SOURCE_FOOTER, "Footer link"),
        (SOURCE_API, "API"),
    ]

    website = models.ForeignKey(
        "websites.Website",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cookie_consent_records",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cookie_consent_records",
    )
    anonymous_id = models.UUIDField(default=uuid.uuid4, db_index=True)

    consent_version = models.CharField(max_length=40, default="2026-06-15")
    policy_version = models.CharField(max_length=40, default="2026-06-15")

    necessary = models.BooleanField(default=True)
    preferences = models.BooleanField(default=False)
    analytics = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_BANNER,
    )
    source_host = models.CharField(max_length=255, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent_hash = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["website", "anonymous_id", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["revoked_at"]),
        ]

    def __str__(self) -> str:
        subject = self.user_id or self.anonymous_id
        website = self.website_id or "global"
        return f"Cookie consent {subject} on {website}"

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def revoke(self, *, save: bool = True) -> None:
        self.revoked_at = timezone.now()
        if save:
            self.save(update_fields=["revoked_at", "updated_at"])
