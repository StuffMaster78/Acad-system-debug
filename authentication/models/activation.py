from django.db import models
from django.utils import timezone
from django.conf import settings

class EmailVerification(models.Model):
    """
    Stores the email verification token for a user (used in link-based verification).
    Can be used alongside OTP.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="email_verification_website"
    )
    token = models.CharField(
        max_length=255,
        unique=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Verification for {self.user.email}"
    
    def is_expired(self):
        expiration_time = timezone.timedelta(hours=24)  # 24-hour expiration
        return timezone.now() > self.created_at + expiration_time
