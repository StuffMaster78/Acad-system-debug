from datetime import timedelta
from django.db import models
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from django.conf import settings


class UserSession(models.Model):
    """
    Tracks user sessions per website for security monitoring and session management.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="user_sessions"
    )
    session_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique identifier for the session."
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address from which the session was created."
    )
    device_type = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text="Device information for session tracking."
    )
    user_agent = models.TextField(
        blank=True, null=True,
        help_text="Full User-Agent string of the client device."
    )
    country = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Geolocation country from IP."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        help_text="Absolute expiration time of the session."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the session is still considered active."
    )

    def __str__(self):
        return (
            f"{self.user.email} | {self.device_type or 'Unknown Device'} | "
            f"{self.session_key} | {self.ip_address or 'Unknown IP'}"
        )

    def is_expired(self):
        """
        Checks if the session has expired due to inactivity (24h timeout).
        Marks the session inactive if expired.
        """
        if self.last_activity < now() - timedelta(hours=24):
            if self.is_active:
                self.is_active = False
                self.save(update_fields=["is_active"])
            return True
        return False

    def terminate(self):
        """
        Terminates the session in the database and Django's session store.
        """
        try:
            Session.objects.get(session_key=self.session_key).delete()
        except Session.DoesNotExist:
            pass

        self.is_active = False
        self.save(update_fields=["is_active"])

    def save(self, *args, **kwargs):
        """
        Prevents duplicate active sessions for the same key and user within a website.
        """
        existing = UserSession.objects.filter(
            session_key=self.session_key,
            website=self.website
        ).exclude(pk=self.pk).first()

        if existing:
            existing.terminate()

        super().save(*args, **kwargs)