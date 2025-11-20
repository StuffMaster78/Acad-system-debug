import hashlib
import uuid

from django.db import models
from django.utils.timezone import now


class TrustedDevice(models.Model):
    """
    Stores trusted devices per user and per website 
    for "Remember This Device" during MFA.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="trusted_devices_user"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="trusted_devices_website"
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
        """
        Check if the device is still trusted.

        Returns:
            bool: True if device is within expiration, else False.
        """
        return self.expires_at > now()

    @staticmethod
    def generate_token():
        """
        Generate a secure, hashed token for identifying the device.

        Returns:
            str: A SHA-256 hashed UUID.
        """
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()