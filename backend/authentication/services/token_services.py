from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.conf import settings
from cryptography.fernet import Fernet # type: ignore

from authentication.models.tokens import SecureToken


class SecureTokenService:
    """
    Manages lifecycle of encrypted tokens per user and website:
    - Creation
    - Secure decryption
    - Expiration enforcement
    - Token rotation
    - Revocation
    """

    def __init__(self, user, website):
        self.user = user
        self.website = website
        self.cipher = Fernet(settings.TOKEN_ENCRYPTION_KEY)

    def create_token(self, raw_token, purpose, expires_in_minutes=10):
        """
        Encrypts and stores a new token for a given purpose.
        """
        encrypted_token = self.cipher.encrypt(raw_token.encode()).decode()
        expires_at = now() + timedelta(minutes=expires_in_minutes)

        return SecureToken.objects.create(
            user=self.user,
            website=self.website,
            encrypted_token=encrypted_token,
            purpose=purpose,
            expires_at=expires_at
        )

    def get_active_token(self, purpose):
        """
        Returns the current active, non-expired token.
        """
        return SecureToken.objects.filter(
            user=self.user,
            website=self.website,
            purpose=purpose,
            is_active=True,
            expires_at__gt=now()
        ).first()

    def revoke_token(self, purpose):
        """
        Revokes the currently active token for a given purpose.
        """
        token = self.get_active_token(purpose)
        if token:
            token.revoke()

    def decrypt_token(self, purpose, rotate=False):
        """
        Decrypts and returns the token's plaintext.
        Optionally rotates it by revoking and issuing a fresh one.

        Returns:
            - if rotate=False: decrypted_token
            - if rotate=True: (decrypted_token, new_token)
        """
        token = self.get_active_token(purpose)
        if not token:
            raise PermissionDenied("Token is invalid, expired, or revoked.")

        decrypted = self.cipher.decrypt(token.encrypted_token.encode()).decode()
        token.revoke()  # 🧨 Revoke to prevent replay

        if rotate:
            remaining_minutes = int((token.expires_at - now()).total_seconds() / 60)
            new_token = self.create_token(
                raw_token=decrypted,
                purpose=purpose,
                expires_in_minutes=remaining_minutes
            )
            return decrypted, new_token

        return decrypted
    
    @staticmethod
    def validate_token(token_str, purpose):
        try:
            token = SecureToken.objects.get(token=token_str, purpose=purpose)
            if token.is_expired():
                return None
            return token
        except SecureToken.DoesNotExist:
            return None

    def rotate_token(self, raw_token, purpose, expires_in_minutes=10):
        """
        Revokes the current token and issues a new one.
        Raw token must be provided by the caller.
        """
        self.revoke_token(purpose)
        return self.create_token(raw_token, purpose, expires_in_minutes)