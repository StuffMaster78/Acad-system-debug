import hashlib
import secrets
from typing import List

from django.utils import timezone
from django.conf import settings
from django.db import transaction

from authentication.models.backup_code import BackupCode
from websites.models import Website


class BackupCodeService:
    """
    Handles generation, validation, and usage of MFA backup codes.
    """

    def __init__(self, user, website):
        """
        Args:
            user (User): The account holder.
            website (Website): The tenant context.
        """
        self.user = user
        self.website = website

    def _hash_code(self, code: str) -> str:
        """
        Hashes a backup code using SHA-256.

        Args:
            code (str): Plaintext backup code.

        Returns:
            str: SHA-256 hash of the code.
        """
        return hashlib.sha256(code.encode()).hexdigest()

    def _generate_plaintext_code(self) -> str:
        """
        Generates a secure random backup code.

        Returns:
            str: A 12-digit numeric code (can adjust format).
        """
        return secrets.token_hex(6)  # 12-character hex string

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generates and stores backup codes for the user.

        Args:
            count (int): Number of codes to generate.

        Returns:
            List[str]: Plaintext backup codes (to show user once).
        """
        plaintext_codes = []

        with transaction.atomic():
            BackupCode.objects.filter(
                user=self.user,
                website=self.website
            ).delete()

            for _ in range(count):
                code = self._generate_plaintext_code()
                hashed = self._hash_code(code)

                BackupCode.objects.create(
                    user=self.user,
                    website=self.website,
                    code_hash=hashed
                )
                plaintext_codes.append(code)

        return plaintext_codes

    def validate_code(self, code: str) -> bool:
        """
        Validates a submitted backup code.

        Args:
            code (str): The plaintext backup code.

        Returns:
            bool: Whether the code is valid and unused.
        """
        hashed = self._hash_code(code)

        try:
            backup_code = BackupCode.objects.get(
                user=self.user,
                website=self.website,
                code_hash=hashed,
                used=False
            )
        except BackupCode.DoesNotExist:
            return False

        backup_code.mark_used()
        return True