# utils/mfa_utils.py
import pyotp
import qrcode
from io import BytesIO
from base64 import b64encode
from django.contrib.auth import get_user_model
from authentication.models.mfa_settings import MFASettings

def generate_totp_qr_code(user_email, issuer_name='Writingsystem'):
    """
    Generate a QR code for setting up TOTP.
    """
    totp = pyotp.TOTP(pyotp.random_base32())
    provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name=issuer_name)

    img = qrcode.make(provisioning_uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_code_base64 = b64encode(buffer.read()).decode('utf-8')
    
    return totp.secret, qr_code_base64

def verify_totp(secret, otp_code):
    """
    Verify the provided OTP code against the secret.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code)

def setup_passkey(user, public_key):
    """
    Setup the passkey (WebAuthn) for the user by storing the public key.
    """
    mfa_settings = MFASettings.objects.get(user=user)
    mfa_settings.passkey_public_key = public_key
    mfa_settings.save()

def verify_passkey_challenge(user, passkey_challenge):
    """
    Verify the passkey challenge for the user.
    """
    mfa_settings = MFASettings.objects.get(user=user)
    
    # Placeholder for actual WebAuthn verification logic
    if passkey_challenge == mfa_settings.passkey_public_key:
        return True
    return False