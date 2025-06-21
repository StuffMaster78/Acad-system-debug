from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FailedLoginAttempt(models.Model):
    """
    Tracks failed login attempts for a user per website.
    Useful for implementing lockout policies.
    """
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="failed_logins"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="failed_login_attempts"
    )
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp} ({self.website})"

    def is_locked_out(self, window_minutes=15, max_attempts=5):
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
        recent_attempts = self.__class__.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=time_threshold
        ).count()
        return recent_attempts >= max_attempts