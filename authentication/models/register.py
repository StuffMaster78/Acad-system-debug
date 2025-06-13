from django.db import models
from django.conf import settings
from django.utils.timezone import now
import uuid

class RegistrationToken(models.Model):
    """
    Handles registration of new users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="registration_tokens"
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        """
        Checks if the registration token is expired.

        Returns:
            bool: True if expired, else False.
        """
        return now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.token}"
    
class RegistrationConfirmationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    website = models.ForeignKey('websites.Website', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    confirmed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)