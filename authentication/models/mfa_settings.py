from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone

class MFASettings(models.Model):
    """
    Stores MFA settings for users, such as which MFA method is selected.
    """
    MFA_METHODS = (
        ('qr_code', 'QR Code (TOTP)'),
        ('passkey', 'Passkey (WebAuthn)'),
        ('email', 'Email Verification'),
        ('sms', 'SMS Verification'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    is_mfa_enabled = models.BooleanField(
        default=False
    )
    mfa_method = models.CharField(
        max_length=50,
        choices=MFA_METHODS,
        default='qr_code',  # Fixed default value
        blank=True,
        null=True
    )
    mfa_phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',  # International phone number format
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    mfa_email_verified = models.BooleanField(
        default=False
    )
    mfa_secret = models.CharField(
        max_length=255, 
        blank=True,
        null=True
    )
    otp_code = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )
    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True
    )
    mfa_recovery_token = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    mfa_recovery_expires = models.DateTimeField(
        blank=True,
        null=True
    )
    passkey_public_key = models.TextField(
        blank=True, null=True
    )
    backup_codes = models.JSONField(
        default=list, blank=True
    )

    def __str__(self):
        return f"MFA settings for {self.user.username}"

    def save(self, *args, **kwargs):
        # Ensure that the recovery token is removed if expired
        if self.mfa_recovery_expires and self.mfa_recovery_expires < timezone.now():
            self.mfa_recovery_token = None
            self.mfa_recovery_expires = None
        super().save(*args, **kwargs)

    def is_otp_valid(self):
        """Check if the OTP is still valid."""
        if self.otp_expires_at and self.otp_code:
            return self.otp_expires_at > timezone.now()
        return False