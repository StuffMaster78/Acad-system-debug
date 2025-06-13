from django.db import models
from django.conf import settings
from django.utils import timezone

class LogoutEvent(models.Model):
    """
    Tracks logout events for auditing and session management.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        'website.Website',
        on_delete=models.CASCADE,
        related_name='logout_events'
    )
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(null=True, blank=True)
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=(
            "Optional reason (e.g., user_initiated, session_expired, admin_kick)"
        )
     )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Logout Event"
        verbose_name_plural = "Logout Events"

    def __str__(self):
        return f"{self.user} logged out at {self.timestamp}"