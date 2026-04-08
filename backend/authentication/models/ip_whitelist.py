from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class IPWhitelist(models.Model):
    """
    User-controlled IP whitelist for restricting logins to trusted IPs.
    Represents the whitelisted IP addresses for a user on a website.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_entries',
        help_text=_("User who owns this whitelist entry")
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name='ip_whitelist_entries',
        help_text=_("Website context")
    )
    ip_address = models.GenericIPAddressField(
        help_text=_("Whitelisted IP address")
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("User-friendly label (e.g., 'Home', 'Office')")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this IP was whitelisted")
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When this IP was last used for login")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this whitelist entry is active")
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website", "ip_address"],
                name="unique_whitelisted_ip_per_user_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "website", "is_active"]),
            models.Index(fields=["ip_address"]),
        ]

    
    def __str__(self):
        label = f" ({self.label})" if self.label else ""
        return f"IP whitelist for {self.user.email}: {self.ip_address}{label}"


class UserIPWhitelistSettings(models.Model):
    """
    Stores the IP whiteliist enforcement settings for a user on a website.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ip_whitelist_settings',
        help_text=_("User whose whitelist settings are configured")
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name='ip_whitelist_settings',
        help_text=_("Website context")
    )
    is_enabled = models.BooleanField(
        default=False,
        help_text=_("Whether IP whitelist is enabled for this user")
    )
    allow_emergency_bypass = models.BooleanField(
        default=True,
        help_text=_("Allow emergency bypass via email verification")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website"],
                name="unique_ip_whitelist_settings_per_user_per_website",
            ),
        ]
    
    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"IP whitelist settings for {self.user.email} - {status}"
