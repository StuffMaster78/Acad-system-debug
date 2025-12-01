import pyotp
import random
import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from authentication.models.mfa_settings import MFASettings
from authentication.models.backup_code import BackupCode


class MFAService:
    """
    Service layer for handling Multi-Factor Authentication logic.
    """

    OTP_EXPIRATION_MINUTES = 5

    def __init__(self, user):
        """
        Args:
            user (User): The user for whom MFA is being managed.
        """
        self.user = user
        self.settings, _ = MFASettings.get_or_create_for_user(user)

    def generate_email_otp(self):
        """
        Generates and stores a 6-digit OTP for email-based 2FA.

        Returns:
            str: The generated OTP code.
        """
        otp = f"{random.randint(100000, 999999)}"
        self.settings.otp_code = otp
        self.settings.otp_expires_at = timezone.now() + timedelta(
            minutes=self.OTP_EXPIRATION_MINUTES
        )
        self.settings.save()
        return otp

    def validate_email_otp(self, code):
        """
        Validates the user's input OTP for email-based 2FA.

        Args:
            code (str): The OTP code entered by the user.

        Raises:
            ValidationError: If the code is incorrect or expired.
        """
        if not self.settings.is_otp_valid():
            raise ValidationError("OTP has expired.")

        if self.settings.otp_code != code:
            raise ValidationError("Invalid OTP code.")

    def generate_totp_secret(self):
        """
        Generates and stores a TOTP secret for QR code MFA.

        Returns:
            str: Base32 secret key for TOTP.
        """
        secret = pyotp.random_base32()
        self.settings.mfa_secret = secret
        self.settings.save()
        return secret

    def validate_totp_code(self, code):
        """
        Validates a TOTP code using the stored secret.

        Args:
            code (str): Code from authenticator app.

        Raises:
            ValidationError: If the code is invalid or expired.
        """
        if not self.settings.mfa_secret:
            raise ValidationError("TOTP not configured.")

        totp = pyotp.TOTP(self.settings.mfa_secret)
        if not totp.verify(code):
            raise ValidationError("Invalid TOTP code.")

    def enable_mfa(self, method):
        """
        Enables MFA with the chosen method.

        Args:
            method (str): 'qr_code', 'email', or 'sms'
        """
        self.settings.is_mfa_enabled = True
        self.settings.mfa_method = method
        self.settings.save()

    def disable_mfa(self):
        """
        Disables all MFA for the user.
        """
        self.settings.is_mfa_enabled = False
        self.settings.mfa_method = None
        self.settings.mfa_secret = None
        self.settings.otp_code = None
        self.settings.otp_expires_at = None
        self.settings.save()

    def generate_backup_codes(self, count=10):
        """
        Creates hashed one-time backup codes.

        Args:
            count (int): Number of codes to generate.

        Returns:
            List[str]: The plain backup codes (store securely).
        """
        from hashlib import sha256

        plain_codes = []
        for _ in range(count):
            code = secrets.token_hex(4)
            plain_codes.append(code)
            BackupCode.objects.create(
                user=self.user,
                code_hash=sha256(code.encode()).hexdigest()
            )
        return plain_codes

    def validate_backup_code(self, code):
        """
        Validates and marks a backup code as used.

        Args:
            code (str): The code entered by user.

        Raises:
            ValidationError: If code is invalid or already used.
        """
        from hashlib import sha256
        code_hash = sha256(code.encode()).hexdigest()

        try:
            backup_code = BackupCode.objects.get(
                user=self.user, code_hash=code_hash, used=False
            )
        except BackupCode.DoesNotExist:
            raise ValidationError("Invalid or already used backup code.")

        backup_code.mark_used()