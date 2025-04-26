from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PasswordResetRequest(models.Model):
    """
    Handles password change requests by users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    token = models.CharField(
        max_length=255,
        unique=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password Reset for {self.user.email}"
    
    def is_expired(self):
        expiration_time = timezone.timedelta(hours=1)  # 1 hour expiration
        return timezone.now() > self.created_at + expiration_time
