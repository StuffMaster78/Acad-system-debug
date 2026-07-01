from __future__ import annotations

import os

from django.conf import settings
from django.db import models


class GatewayMode(models.TextChoices):
    LIVE = "live", "Live"
    TEST = "test", "Test"


class PaymentGatewayConfig(models.Model):
    """
    Per-website payment gateway configuration.

    One row per website — controls which provider handles payments, the
    webhook endpoint Stripe should POST to, the callback base URL Stripe
    redirects clients to after checkout, and whether the gateway is in
    live or test mode.

    Secrets are never stored in the database. Instead, set the *name* of
    the environment variable that holds each secret:
        secret_key_env_var      → e.g. "STRIPE_SECRET_KEY_NURSEMYGRADE"
        webhook_secret_env_var  → e.g. "STRIPE_WEBHOOK_SECRET_NURSEMYGRADE"

    Leave either field blank to inherit the platform default
    (STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET from Django settings).
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="payment_gateway_config",
    )
    gateway = models.CharField(
        max_length=32,
        default="stripe",
        help_text="Provider name — must match a registered provider key (e.g. 'stripe').",
    )
    webhook_endpoint = models.CharField(
        max_length=255,
        default="/api/payments/webhooks/stripe/",
        help_text=(
            "Full path registered in the Stripe dashboard for this site. "
            "For per-site routing use /api/payments/webhooks/stripe/<site-slug>/."
        ),
    )
    callback_base_url = models.URLField(
        max_length=255,
        blank=True,
        default="",
        help_text=(
            "Base URL Stripe redirects clients to after checkout "
            "(e.g. https://app.gradecrest.com). "
            "Leave blank to fall back to Website.root_url."
        ),
    )
    mode = models.CharField(
        max_length=8,
        choices=GatewayMode.choices,
        default=GatewayMode.LIVE,
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive gateways fall back to the platform default.",
    )

    # ── Per-site credential routing ──────────────────────────────────────────
    secret_key_env_var = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text=(
            "Name of the environment variable that holds this site's Stripe secret key "
            "(e.g. STRIPE_SECRET_KEY_NURSEMYGRADE). "
            "Leave blank to use the platform default STRIPE_SECRET_KEY."
        ),
    )
    webhook_secret_env_var = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text=(
            "Name of the environment variable that holds this site's Stripe webhook "
            "signing secret (e.g. STRIPE_WEBHOOK_SECRET_NURSEMYGRADE). "
            "Leave blank to use the platform default STRIPE_WEBHOOK_SECRET."
        ),
    )
    statement_descriptor = models.CharField(
        max_length=22,
        blank=True,
        default="",
        help_text=(
            "Statement descriptor sent to Stripe for every payment on this site — "
            "what appears on the cardholder's bank statement. Max 22 chars, "
            "Latin characters only, no < > \\ ' \" * characters. "
            "Leave blank to use the Stripe account default."
        ),
    )

    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gateway_config_updates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Gateway Config"
        verbose_name_plural = "Payment Gateway Configs"

    def __str__(self) -> str:
        return f"{self.website.name} — {self.gateway} ({self.mode})"

    @property
    def effective_callback_base_url(self) -> str:
        return (
            self.callback_base_url.rstrip("/")
            or getattr(self.website, "root_url", "").rstrip("/")
        )

    @property
    def effective_secret_key(self) -> str:
        """Resolve the Stripe secret key for this site, or fall back to platform default."""
        if self.secret_key_env_var:
            val = os.environ.get(self.secret_key_env_var, "")
            if val:
                return val
        return getattr(settings, "STRIPE_SECRET_KEY", "")

    @property
    def effective_webhook_secret(self) -> str:
        """Resolve the Stripe webhook secret for this site, or fall back to platform default."""
        if self.webhook_secret_env_var:
            val = os.environ.get(self.webhook_secret_env_var, "")
            if val:
                return val
        return getattr(settings, "STRIPE_WEBHOOK_SECRET", "")


class PaymentNotificationEmail(models.Model):
    """
    Email addresses that receive forwarded payment notification emails
    for a given website.

    Multiple rows per website are allowed (e.g. finance team + CEO).
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="payment_notification_emails",
    )
    email = models.EmailField()
    label = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Optional label, e.g. 'Finance team' or 'CEO'.",
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_notification_email_creations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Notification Email"
        verbose_name_plural = "Payment Notification Emails"
        unique_together = [("website", "email")]
        ordering = ["website__name", "email"]

    def __str__(self) -> str:
        return f"{self.email} → {self.website.name}"
