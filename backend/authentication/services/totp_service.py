import base64
import io
import secrets
from typing import Any
from PIL.Image import Image
import pyotp
import qrcode
from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.mfa_device import MFADevice


class TOTPService:
    """
    Handle TOTP setup and verification for MFA devices.

    This service is responsible for:
        - generating TOTP secrets
        - building provisioning URIs
        - verifying submitted TOTP codes
        - generating QR code images for authenticator apps

    Notes:
        - TOTP secrets must be encrypted at rest.
        - TOTP codes are not stored in the database.
        - Verification is performed against the device secret.
    """

    ISSUER_NAME = "YourApp"

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new base32 TOTP secret.

        Returns:
            A base32-encoded secret string.
        """
        return pyotp.random_base32()

    @staticmethod
    def build_totp(secret: str) -> pyotp.TOTP:
        """
        Build a TOTP instance from a secret.

        Args:
            secret: Base32 TOTP secret.

        Returns:
            A pyotp.TOTP instance.
        """
        return pyotp.TOTP(secret)

    @classmethod
    def build_provisioning_uri(
        cls,
        *,
        user_identifier: str,
        secret: str,
        issuer_name: str | None = None,
    ) -> str:
        """
        Build a TOTP provisioning URI for authenticator apps.

        Args:
            user_identifier: User label shown in the authenticator app.
            secret: Base32 TOTP secret.
            issuer_name: Optional issuer name override.

        Returns:
            A provisioning URI string.
        """
        issuer = issuer_name or cls.ISSUER_NAME
        totp = cls.build_totp(secret)

        return totp.provisioning_uri(
            name=user_identifier,
            issuer_name=issuer,
        )

    @classmethod
    def generate_qr_code_base64(
        cls,
        *,
        provisioning_uri: str,
    ) -> str:
        """
        Generate a base64-encoded PNG QR code for a provisioning URI.

        Args:
            provisioning_uri: TOTP provisioning URI.

        Returns:
            A base64-encoded PNG image string.
        """
        qr_image: Image = qrcode.make(provisioning_uri) # type: ignore

        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return encoded

    @classmethod
    def initialize_totp_device(
        cls,
        *,
        user,
        website,
        name: str = "Authenticator App",
        issuer_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new unverified TOTP MFA device and setup payload.

        Args:
            user: User instance.
            website: Website instance.
            name: Human-readable device name.
            issuer_name: Optional issuer name override.

        Returns:
            A dictionary containing:
                - device: MFADevice instance
                - secret: raw TOTP secret
                - provisioning_uri: otpauth URI
                - qr_code_base64: base64 PNG QR code
        """
        secret = cls.generate_secret()

        device = MFADevice.objects.create(
            user=user,
            website=website,
            method=MFADevice.Method.TOTP,
            name=name,
            secret=secret,
            is_verified=False,
            is_active=True,
        )

        user_identifier = getattr(user, "email", None) or str(user)

        provisioning_uri = cls.build_provisioning_uri(
            user_identifier=user_identifier,
            secret=secret,
            issuer_name=issuer_name,
        )

        qr_code_base64 = cls.generate_qr_code_base64(
            provisioning_uri=provisioning_uri,
        )

        return {
            "device": device,
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "qr_code_base64": qr_code_base64,
        }

    @staticmethod
    def verify_code(
        *,
        device: MFADevice,
        code: str,
        valid_window: int = 1,
    ) -> bool:
        """
        Verify a submitted TOTP code against a device secret.

        Args:
            device: MFADevice instance.
            code: Submitted TOTP code.
            valid_window: Number of adjacent time steps to allow.

        Returns:
            True if the code is valid, otherwise False.

        Raises:
            ValidationError: If the device is not a TOTP device or
                does not have a secret configured.
        """
        if device.method != MFADevice.Method.TOTP:
            raise ValidationError(
                "The selected MFA device is not a TOTP device."
            )

        if not device.secret:
            raise ValidationError(
                "This TOTP device does not have a secret configured."
            )

        totp = pyotp.TOTP(device.secret)
        return bool(
            totp.verify(code, valid_window=valid_window)
        )

    @classmethod
    @transaction.atomic
    def verify_and_activate_device(
        cls,
        *,
        device: MFADevice,
        code: str,
        valid_window: int = 1,
    ) -> MFADevice:
        """
        Verify a TOTP code and mark the device as verified.

        This is typically used during initial TOTP setup.

        Args:
            device: MFADevice instance.
            code: Submitted TOTP code.
            valid_window: Number of adjacent time steps to allow.

        Returns:
            The verified MFADevice instance.

        Raises:
            ValidationError: If the submitted code is invalid.
        """
        is_valid = cls.verify_code(
            device=device,
            code=code,
            valid_window=valid_window,
        )

        if not is_valid:
            raise ValidationError("Invalid authenticator code.")

        device.mark_as_verified()
        device.mark_as_used()

        return device

    @classmethod
    @transaction.atomic
    def authenticate_with_totp(
        cls,
        *,
        device: MFADevice,
        code: str,
        valid_window: int = 1,
    ) -> MFADevice:
        """
        Authenticate a user using an already verified TOTP device.

        Args:
            device: MFADevice instance.
            code: Submitted TOTP code.
            valid_window: Number of adjacent time steps to allow.

        Returns:
            The MFADevice instance.

        Raises:
            ValidationError: If the device is inactive, unverified,
                or the code is invalid.
        """
        if not device.is_active:
            raise ValidationError("This MFA device is inactive.")

        if not device.is_verified:
            raise ValidationError("This MFA device is not verified.")

        is_valid = cls.verify_code(
            device=device,
            code=code,
            valid_window=valid_window,
        )

        if not is_valid:
            raise ValidationError("Invalid authenticator code.")

        device.mark_as_used()

        return device

    @staticmethod
    def generate_recovery_key(length: int = 32) -> str:
        """
        Generate a recovery-style random string.

        Args:
            length: Desired number of bytes before URL-safe encoding.

        Returns:
            A secure URL-safe recovery string.
        """
        return secrets.token_urlsafe(length)