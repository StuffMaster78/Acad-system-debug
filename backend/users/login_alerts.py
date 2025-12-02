"""
Login Alert Preferences Model
Allows users to configure email/push notifications for security events.
"""
from django.db import models
from django.conf import settings
from websites.models import Website


class LoginAlertPreference(models.Model):
    """
    User preferences for login-related security alerts.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_alert_preferences'
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='login_alert_preferences'
    )
    
    # Alert toggles
    notify_new_login = models.BooleanField(
        default=True,
        help_text="Notify when a new login occurs"
    )
    notify_new_device = models.BooleanField(
        default=True,
        help_text="Notify when login from a new device"
    )
    notify_new_location = models.BooleanField(
        default=True,
        help_text="Notify when login from a new location"
    )
    
    # Channel preferences
    email_enabled = models.BooleanField(
        default=True,
        help_text="Receive alerts via email"
    )
    push_enabled = models.BooleanField(
        default=False,
        help_text="Receive alerts via push notifications"
    )
    in_app_enabled = models.BooleanField(
        default=True,
        help_text="Receive alerts in-app"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'website')
        verbose_name = "Login Alert Preference"
        verbose_name_plural = "Login Alert Preferences"
        indexes = [
            models.Index(fields=['user', 'website']),
        ]
    
    def __str__(self):
        return f"Login Alerts for {self.user.email} on {self.website.domain}"

