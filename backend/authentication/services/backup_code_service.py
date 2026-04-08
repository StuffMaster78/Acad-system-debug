from typing import List

from django.db import transaction

from authentication.models.backup_code import BackupCode
from authentication.services.token_service import TokenService


class BackupCodeService:
    """
    Handle generation, validation, and consumption of MFA backup codes.

    Backup codes are single-use fallback credentials for multi-factor
    authentication. Raw codes are generated once, shown to the user,
    and never stored directly in the database.
    """

    DEFAULT_CODE_COUNT = 10
    CODE_TOKEN_BYTES = 6

    def __init__(self, user, website):
        """
        Initialize the backup code service.

        Args:
            user: The account holder.
            website: The tenant or website context.
        """
        self.user = user
        self.website = website

    @staticmethod
    def _generate_plaintext_code() -> str:
        """
        Generate a secure backup code.

        Returns:
            A URL-safe backup code string.
        """
        return TokenService.generate_token(nbytes=6)

    @staticmethod
    def _hash_code(code: str) -> str:
        """
        Hash a backup code before persistence.

        Args:
            code: Plaintext backup code.

        Returns:
            A hexadecimal SHA-256 hash of the backup code.
        """
        return TokenService.hash_value(code)

    @transaction.atomic
    def generate_backup_codes(
        self,
        count: int = DEFAULT_CODE_COUNT,
    ) -> List[str]:
        """
        Generate and store a new set of backup codes for the user.

        Existing backup codes for the same user and website are removed
        before the new set is created.

        Args:
            count: Number of backup codes to generate.

        Returns:
            A list of plaintext backup codes. These should be shown to
            the user once and not stored elsewhere in plaintext.
        """
        plaintext_codes: List[str] = []

        BackupCode.objects.filter(
            user=self.user,
            website=self.website,
        ).delete()

        backup_code_objects = []

        for _ in range(count):
            code = self._generate_plaintext_code()
            code_hash = self._hash_code(code)

            plaintext_codes.append(code)
            backup_code_objects.append(
                BackupCode(
                    user=self.user,
                    website=self.website,
                    code_hash=code_hash,
                )
            )

        BackupCode.objects.bulk_create(backup_code_objects)

        return plaintext_codes

    @transaction.atomic
    def validate_code(
        self,
        code: str,
    ) -> bool:
        """
        Validate and consume a submitted backup code.

        Args:
            code: The plaintext backup code submitted by the user.

        Returns:
            True if the backup code is valid and successfully consumed.
            False otherwise.
        """
        code_hash = self._hash_code(code)

        backup_code = BackupCode.objects.filter(
            user=self.user,
            website=self.website,
            code_hash=code_hash,
            used_at__isnull=True,
        ).first()

        if backup_code is None:
            return False

        backup_code.mark_as_used()
        return True