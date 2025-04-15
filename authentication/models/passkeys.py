"""
Models for storing passkey (WebAuthn) credentials for passwordless login.
"""

from django.db import models
from django.conf import settings


class WebAuthnCredential(models.Model):
    """
    Stores public key credentials registered by the user for passkey-based login.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="webauthn_credentials"
    )
    credential_id = models.CharField(
        max_length=255, unique=True,
        help_text="Base64URL-encoded credential ID registered via WebAuthn"
    )
    public_key = models.TextField(
        help_text="User's public key from the authenticator device"
    )
    sign_count = models.PositiveIntegerField(
        default=0,
        help_text="Monotonic counter used to detect cloned credentials"
    )
    transports = models.JSONField(
        default=list,
        help_text="List of transport methods like 'usb', 'nfc', 'ble', 'internal'"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Passkey for {self.user} (cred_id={self.credential_id[:8]}...)"