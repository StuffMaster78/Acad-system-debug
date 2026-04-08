from django.conf import settings
from django.db import models
from django.utils import timezone


class MFADevice(models.Model):
    """
    Represent a registered multi-factor authentication device.

    This model stores a user's MFA method configuration, such as a TOTP
    authenticator app, email OTP, or SMS OTP. Sensitive secrets should
    be stored securely and handled carefully at the service layer.
    """

    class Method(models.TextChoices):
        TOTP = "totp", "Authenticator App"
        EMAIL = "email", "Email OTP"
        SMS = "sms", "SMS OTP"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_devices",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="mfa_devices",
    )
    method = models.CharField(
        max_length=32,
        choices=Method.choices,
        help_text="MFA method used by this device.",
    )
    name = models.CharField(
        max_length=100,
        help_text="User-friendly label for the MFA device.",
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Secret associated with the MFA device. For TOTP, this is "
            "the shared secret used to generate codes."
        ),
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        help_text="Phone number used for SMS-based MFA, if applicable.",
    )
    email = models.EmailField(
        blank=True,
        help_text="Email used for email-based MFA, if applicable.",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the user's primary MFA device.",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this MFA device has been verified.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this MFA device is currently active.",
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this device was last used.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "MFA Device"
        verbose_name_plural = "MFA Devices"
        indexes = [
            models.Index(fields=["user", "website"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["user", "is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website", "name"],
                name="unique_mfa_device_name_per_user_per_website",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the MFA device.
        """
        return (
            f"MFA device '{self.name}' for {self.user} "
            f"({self.method})"
        )

    def mark_as_used(self) -> None:
        """
        Update the device's last-used timestamp.
        """
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    def activate(self) -> None:
        """
        Activate the MFA device.
        """
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active"])

    def deactivate(self) -> None:
        """
        Deactivate the MFA device.
        """
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])

    def mark_as_verified(self) -> None:
        """
        Mark the MFA device as verified.
        """
        if not self.is_verified:
            self.is_verified = True
            self.save(update_fields=["is_verified"])