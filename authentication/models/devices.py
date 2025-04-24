import hashlib
import uuid

from django.db import models
from django.utils.timezone import now
# from django.conf import settings
from users.models import User


class TrustedDevice(models.Model):
    """
    Stores trusted devices for users who selected
    "Remember This Device" during MFA.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="trusted_devices"
    )
    device_token = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed token for the trusted device."
    )
    device_info = models.TextField(
        help_text="Device user-agent or metadata for tracking."
    )
    last_used = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        help_text="Expiration time for trusted device."
    )

    def is_valid(self):
        """Checks if the device is still trusted."""
        return self.expires_at > now()

    @staticmethod
    def generate_token():
        """Generates a secure hashed token."""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
