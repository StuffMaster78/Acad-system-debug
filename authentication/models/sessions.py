from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from django.conf import settings
from users.models import User


class UserSession(models.Model):
    """
    Tracks active user sessions for security monitoring.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    session_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique identifier for the session."
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the session."
    )
    device_type = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text="Device information for session tracking."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    expires_at = models.DateTimeField(
        help_text="When this session will expire."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is the session currently active?"
    )
    user_agent = models.TextField(blank=True, null=True)
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.session_key} - {self.ip_address}"
    
    def is_expired(self):
        """Checks if the session is expired due to 24 hours of inactivity."""
        expired = self.last_activity < now() - timedelta(hours=24)
        if expired and self.is_active:
            self.is_active = False
            self.save()
        return expired

    
    def terminate(self):
        """Terminate the session."""
        from django.contrib.sessions.models import Session
        try:
            session = Session.objects.get(
                session_key=self.session_key
            )
            session.delete()
        except Session.DoesNotExist:
            pass

        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        """
        Prevents duplicate sessions by terminating any existing session
        before saving a new one.
        """
        UserSession.objects.update_or_create(
        session_key=self.session_key,
        defaults={
            "user": self.user,
            "ip_address": self.ip_address,
            "device_type": self.device_type
            },
        )
        super().save(*args, **kwargs)