"""
Security Events Model - Comprehensive security event tracking.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class SecurityEvent(models.Model):
    """
    Comprehensive security event tracking for user transparency.
    """
    
    EVENT_TYPE_CHOICES = [
        ('login', 'Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('2fa_verified', '2FA Verified'),
        ('magic_link_used', 'Magic Link Used'),
        ('device_trusted', 'Device Trusted'),
        ('device_revoked', 'Device Revoked'),
        ('session_created', 'Session Created'),
        ('session_revoked', 'Session Revoked'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('suspicious_session_reported', 'Suspicious Session Reported'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('profile_updated', 'Profile Updated'),
        ('privacy_settings_changed', 'Privacy Settings Changed'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='security_events',
        help_text=_("User this event belongs to")
    )
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='security_events',
        help_text=_("Website this event occurred on")
    )
    
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        help_text=_("Type of security event")
    )
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='low',
        help_text=_("Severity of the event")
    )
    
    is_suspicious = models.BooleanField(
        default=False,
        help_text=_("Whether this event is suspicious")
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address of the event")
    )
    
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Geographic location (city, country)")
    )
    
    device = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Device information")
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text=_("User agent string")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the event occurred")
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional event metadata")
    )
    
    class Meta:
        verbose_name = _("Security Event")
        verbose_name_plural = _("Security Events")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['is_suspicious', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event_type} at {self.created_at}"
    
    @classmethod
    def log_event(cls, user, website, event_type, severity='low', is_suspicious=False,
                  ip_address=None, location=None, device=None, user_agent=None, metadata=None):
        """
        Create a security event log entry.
        """
        return cls.objects.create(
            user=user,
            website=website,
            event_type=event_type,
            severity=severity,
            is_suspicious=is_suspicious,
            ip_address=ip_address,
            location=location,
            device=device,
            user_agent=user_agent,
            metadata=metadata or {}
        )

