from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class FailedLoginAttempt(models.Model):
    """
    Tracks failed login attempts for a user per website.
    Useful for implementing lockout policies.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="failed_logins"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="failed_login_attempts"
    )
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    asn = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp} ({self.website})"
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ('user', 'website', 'timestamp')
        indexes = [
            models.Index(fields=["user", "website", "timestamp"]),
        ]

    def is_locked_out(cls, user, website, window_minutes=15, max_attempts=5):
        """
        Determines if the user is locked out on this website.

        Args:
            window_minutes (int): Time window to consider.
            max_attempts (int): Max allowed failed attempts in window.

        Returns:
            bool: True if locked out, else False.
        """
        time_threshold = timezone.now() - timezone.timedelta(
            minutes=window_minutes
        )
        recent_attempts = cls.objects.filter(
            user=user,
            website=website,
            timestamp__gte=time_threshold
        ).count()
        return recent_attempts >= max_attempts