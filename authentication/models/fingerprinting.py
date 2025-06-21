"""
Model for tracking device/browser
fingerprints for trust and risk analysis.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

class DeviceFingerprint(models.Model):
    """
    Stores browser/device fingerprint
    for session validation and fraud scoring.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="fingerprints_user"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="device_fingerprints"
    )
    fingerprint_hash = models.CharField(
        max_length=255,
        help_text="Hash of the device fingerprint (e.g., from FingerprintJS)"
    )
    user_agent = models.TextField(
        help_text="Full user agent string of the client browser/device"
    )
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    trusted = models.BooleanField(default=False)
    trust_score = models.FloatField(default=0.0)
    login_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        trust_status = "trusted" if self.trusted else "untrusted"
        return f"{self.user} - {trust_status} fingerprint"
    
    def is_expired(self, hours=48):
        """Checks if the fingerprint is too old to trust."""
        return self.created_at < timezone.now() - timezone.timedelta(hours=hours)