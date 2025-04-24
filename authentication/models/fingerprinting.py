"""
Model for browser or device fingerprinting used in risk scoring or trust decisions.
"""

from django.db import models
from django.conf import settings


class DeviceFingerprint(models.Model):
    """
    Stores a browser/device fingerprint for fraud
    prevention and session validation.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="fingerprints"
    )
    fingerprint_hash = models.CharField(
        max_length=255,
        help_text="Hash of the device fingerprint (e.g., from FingerprintJS)"
    )
    user_agent = models.TextField(
        help_text="Full user agent string of the browser or client device"
    )
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    trusted = models.BooleanField(default=False)

    def __str__(self):
        return f"Fingerprint for {self.user} ({'trusted' if self.trusted else 'untrusted'})"