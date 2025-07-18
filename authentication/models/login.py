from django.db import models
from django.conf import settings
from django.utils.timezone import now

class LoginSession(models.Model):
    """
    Model representing a user's login session on a website.
    Stores information about the user, the website, and the session details.
    This model is used to track user logins, including device and IP information,
    and to manage active sessions for security purposes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="login_sessions"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(null=True, blank=True)
    device_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    logged_in_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True)
    token = models.CharField(
        max_length=255,
        unique=True
    )

    class Meta:
        ordering = ['-logged_in_at']

    def __str__(self):
        return f"{self.user} - {self.ip_address} - {self.device_name}"