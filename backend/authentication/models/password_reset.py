import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PasswordResetRequest(models.Model):
    """
    Handles password change requests by users.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='password_resets'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    token = models.CharField(
        max_length=255,
        unique=True
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(
        default=timezone.now
    )
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password Reset for {self.user.email}"
    
    @staticmethod
    def generate_otp():
        return f"{random.randint(100000, 999999)}"
    
    def is_expired(self):
        """
        Returns True if the token is expired (after 1 hour).
        """
        expiration_time = timezone.timedelta(hours=1)  # 1 hour expiration
        return timezone.now() > self.created_at + expiration_time
