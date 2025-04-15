from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied

from cryptography.fernet import Fernet



class SecureToken(models.Model):
    """
    Stores API tokens securely using encryption.
    """
    TOKEN_PURPOSE_CHOICES = [
        ("api_key", "API Key"),
        ("refresh_token", "JWT Refresh Token"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="tokens"
    )
    encrypted_token = models.TextField(
        help_text="Encrypted API token."
    )
    purpose = models.CharField(
        max_length=20,
        choices=TOKEN_PURPOSE_CHOICES, 
        help_text="Purpose of the token."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this token will expire."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this token currently active?"
    )

    def encrypt_token(self, raw_token):
        """Encrypts the token before saving."""
        cipher = Fernet(TOKEN_ENCRYPTION_KEY)
        encrypted = cipher.encrypt(raw_token.encode())
        return encrypted.decode()

    def decrypt_token(self):
        """Decrypts and returns the original token only
        if it's still active and not expired.
        """
        if not self.is_active or self.expires_at < now():
            raise PermissionDenied("This token is expired or revoked.")

        cipher = Fernet(TOKEN_ENCRYPTION_KEY)
        decrypted = cipher.decrypt(self.encrypted_token.encode())
        self.revoke() # Revoke the token after use to prevent replay attacks
        return decrypted.decode()

    def revoke(self):
        """Revokes the token."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - Active: {self.is_active}"
    

class SecureTokenManager(models.Manager):
    def create_encrypted_token(self, user, refresh_token):
        """Encrypts and stores the refresh token securely."""
        cipher = Fernet(FERNET_KEY)
        encrypted_token = cipher.encrypt(refresh_token.encode())

        return self.create(user=user, encrypted_token=encrypted_token.decode())

    def decrypt_token(self, encrypted_token):
        """Decrypts an encrypted refresh token."""
        cipher = Fernet(FERNET_KEY)
        return cipher.decrypt(encrypted_token.encode()).decode()

class EncryptedRefreshToken(models.Model):
    """Stores encrypted refresh tokens securely."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    encrypted_token = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = SecureTokenManager()

    def __str__(self):
        return f"Token for {self.user.email}"