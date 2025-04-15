from django.db import models
from django.contrib.auth.models import User

class MFASettings(models.Model):
    """
    Stores MFA settings for users, such as which MFA method is selected.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    is_mfa_enabled = models.BooleanField(
        default=False
    )
    mfa_method = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('totp', 'TOTP')],
        blank=True,
        null=True
    )
    mfa_phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )  # For SMS-based MFA
    mfa_email_verified = models.BooleanField(
        default=False
    )  # To track email-based verification

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
    

    
    def __str__(self):
        return f"MFA settings for {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)