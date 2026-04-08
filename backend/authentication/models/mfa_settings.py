from django.conf import settings
from django.db import models


class MFASettings(models.Model):
    """
    Store MFA preferences and enforcement settings for a user within
    a website context.

    This model holds policy and preference data only. Device-specific
    secrets, challenge codes, recovery tokens, and backup codes should
    live in dedicated models.
    """

    class MFAMethod(models.TextChoices):
        TOTP = "totp", "Authenticator App"
        EMAIL = "email", "Email Verification"
        SMS = "sms", "SMS Verification"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_settings",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="mfa_settings",
    )
    is_enabled = models.BooleanField(
        default=False,
        help_text="Whether MFA is enabled for this user.",
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Whether MFA is mandatory for this user.",
    )
    preferred_method = models.CharField(
        max_length=32,
        choices=MFAMethod.choices,
        blank=True,
        null=True,
        help_text="Preferred MFA method for the user.",
    )
    allow_totp = models.BooleanField(
        default=True,
        help_text="Whether TOTP authenticator apps are allowed.",
    )
    allow_email = models.BooleanField(
        default=True,
        help_text="Whether email-based MFA is allowed.",
    )
    allow_sms = models.BooleanField(
        default=False,
        help_text="Whether SMS-based MFA is allowed.",
    )
    remember_device_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of days to remember trusted devices.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "MFA Settings"
        verbose_name_plural = "MFA Settings"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website"],
                name="unique_mfa_settings_per_user_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "is_enabled"]),
            models.Index(fields=["user", "website"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the MFA settings.
        """
        return f"MFA settings for {self.user} on {self.website}"