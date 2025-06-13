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
        ('email', 'Email Verification'),
        ('sms', 'SMS Verification'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='mfa_settings'
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
                regex=r'^\+?1?\d{9,15}$',
                message=(
                    "Phone number must be in format: '+999999999'. "
                    "Up to 15 digits allowed."
                )
            )
        ]
    )
    
    mfa_email_verified = models.BooleanField(
        default=False
    )

     # TOTP secret key
    mfa_secret = models.CharField(
        max_length=255, 
        blank=True,
        null=True
    )
     # Temporary OTPs for email/sms
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

     # Recovery codes
    backup_codes = models.JSONField(
        default=list, blank=True
    )

    def __str__(self):
        return f"MFA settings for {self.user.username}"

    def save(self, *args, **kwargs):
        """
        Clears the recovery token if it's expired before saving.
        """
        # Ensure that the recovery token is removed if expired
        if self.mfa_recovery_expires and self.mfa_recovery_expires < timezone.now():
            self.mfa_recovery_token = None
            self.mfa_recovery_expires = None
        super().save(*args, **kwargs)

    def is_otp_valid(self):
        """
        Checks if the current OTP is still valid.

        Returns:
            bool: True if OTP is valid, False otherwise.
        """
        if self.otp_expires_at and self.otp_code:
            return self.otp_expires_at > timezone.now()
        return False