"""
Session Limit Models
Handles concurrent session limits and management.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class SessionLimitPolicy(models.Model):
    """
    Defines session limit policies for users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_limit_policy',
        help_text=_("User whose session limits are configured")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='session_limit_policies',
        help_text=_("Website context")
    )
    max_concurrent_sessions = models.IntegerField(
        default=3,
        help_text=_("Maximum number of concurrent active sessions")
    )
    allow_unlimited_trusted = models.BooleanField(
        default=False,
        help_text=_("Allow unlimited sessions from trusted devices")
    )
    revoke_oldest_on_limit = models.BooleanField(
        default=True,
        help_text=_("Revoke oldest session when limit is reached")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['website', 'user']),
        ]
        verbose_name = _("Session Limit Policy")
        verbose_name_plural = _("Session Limit Policies")
    
    def __str__(self):
        return f"Session limit for {self.user.email}: {self.max_concurrent_sessions} sessions"

