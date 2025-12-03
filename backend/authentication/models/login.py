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
    last_activity = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='revoked_sessions'
    )
    is_active = models.BooleanField(default=True)
    token = models.CharField(
        max_length=255,
        unique=True
    )

    class Meta:
        ordering = ['-logged_in_at']
        indexes = [
            models.Index(fields=['user', 'website', 'is_active']),
            models.Index(fields=['token']),
        ]

    def revoke(self, revoked_by=None):
        """Revoke this session."""
        from django.utils import timezone
        self.is_active = False
        self.revoked_at = timezone.now()
        if revoked_by:
            self.revoked_by = revoked_by
        self.save(update_fields=['is_active', 'revoked_at', 'revoked_by'])
    
    def __str__(self):
        return f"{self.user} - {self.ip_address} - {self.device_name}"