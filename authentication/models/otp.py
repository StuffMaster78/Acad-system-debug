from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class OTP(models.Model):
    """
    Represents a One-Time Password (OTP) for user authentication.
    This model is used to store OTPs generated for users.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        help_text="the website getting the OTP"
        )
    otp_code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(
        max_length=50,
        help_text=("Purpose of the OTP, e.g., 'login', 'mfa', 'password_reset'")
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'otp_code']),
        ]

    def is_expired(self):
        return timezone.now() > self.expiration_time

    def __str__(self):
        return f"OTP for {self.user} - Expires at {self.expiration_time}"
