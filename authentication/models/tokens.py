from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied

from cryptography.fernet import Fernet # type: ignore



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
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="secure_tokens"
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
    def create_token(self, user, website, raw_token, purpose, expires_at):
        """
        Creates and stores a new encrypted token.
        """
        cipher = Fernet(FERNET_KEY)
        encrypted_token = cipher.encrypt(raw_token.encode()).decode()
        return self.create(
            user=user,
            website=website,
            encrypted_token=encrypted_token,
            purpose=purpose,
            expires_at=expires_at,
        )

    def decrypt(self, encrypted_token: str) -> str:
        """
        Utility for decrypting tokens without model instance.
        """
        cipher = Fernet(FERNET_KEY)
        return cipher.decrypt(encrypted_token.encode()).decode()

class EncryptedRefreshToken(models.Model):
    """Stores encrypted refresh tokens securely."""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="secure_website_tokens"
    )
    encrypted_token = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = SecureTokenManager()

    def __str__(self):
        return f"Token for {self.user.email}"