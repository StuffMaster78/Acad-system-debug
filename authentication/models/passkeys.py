from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

class WebAuthnCredential(models.Model):
    """
    Stores public key credentials registered by the user for passkey-based
    login.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="webauthn_credentials"
    )
    credential_id = models.TextField(  # Changed to TextField to handle longer IDs
        unique=True,
        help_text="Base64URL-encoded credential ID registered via WebAuthn"
    )
    public_key = models.BinaryField(  # Changed to BinaryField for raw public key
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
    device_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    device_fingerprint = models.CharField(
        max_length=64, blank=True, null=True
    )
    device_label = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    device_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Human-readable device name (user-editable)."
    )
    is_device_name_custom = models.BooleanField(
        default=False,
        help_text="If True, user manually edited device name."
    )

    def __str__(self):
        return f"Passkey for {self.user} (cred_id={self.credential_id[:8]}...)"

    def increment_sign_count(self):
        """Increment the sign count after successful authentication."""
        self.sign_count += 1
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['user']),  # Index user for better lookup performance
        ]
