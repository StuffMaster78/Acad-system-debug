import pyotp
import qrcode
from io import BytesIO
import base64

class TOTPService:
    """
    Handles TOTP (Time-based One-Time Password) 2FA setup and verification.
    """

    @staticmethod
    def generate_totp_secret():
        """
        Generates a secure base32 secret for TOTP.
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(username, secret, issuer="YourApp"):
        """
        Generates a base64-encoded PNG QR code for user setup.

        Args:
            username (str): Typically user's email or username.
            secret (str): TOTP secret.
            issuer (str): Issuer name for the QR code.

        Returns:
            str: Base64 encoded QR code image.
        """
        uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
        img = qrcode.make(uri)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def verify_totp(secret, code):
        """
        Verifies a TOTP code.

        Args:
            secret (str): TOTP shared secret.
            code (str): The OTP code to verify.

        Returns:
            bool: Whether the code is valid.
        """
        return pyotp.TOTP(secret).verify(code)