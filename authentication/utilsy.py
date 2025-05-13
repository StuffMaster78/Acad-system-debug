import random
import string
import hashlib
import pyotp
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from celery import shared_task 
from django.apps import apps
from authentication.models.otp import OTP
from authentication.models.magic_links import MagicLink
from rest_framework.exceptions import AuthenticationFailed
from websites.models import WebsiteSettings, Website
from ipware import get_client_ip # type: ignore
from authentication.models.logout import LogoutEvent
from users.models import User
import jwt # type: ignore
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings


def get_client_ip(request):
    ip, is_routable = get_client_ip(request)
    return ip


def encode_verification_token(user, expiry_minutes=30):
    """
    Generate a JWT token for email verification or similar use.
    
    Args:
        user (User): The user instance to encode into the token.
        expiry_minutes (int): Minutes until the token expires.

    Returns:
        str: Encoded JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    payload = {
        'user_id': user.id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'type': 'verification'
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    # jwt.encode returns a bytestring in PyJWT < 2.0, string in >= 2.0
    return token if isinstance(token, str) else token.decode('utf-8')

def decode_verification_token(token):
    """
    Decode the JWT token to get user data (e.g., user ID) and validate the token.
    """
    try:
        # Decode the token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )

        # Get user from decoded payload (e.g., user ID)
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)

        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('The verification token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')
    except User.DoesNotExist:
        raise AuthenticationFailed('User not found.')

def send_custom_email(user, subject, body, website_id):
    sender_name, sender_email, _ = get_email_sender_details(website_id)
    send_mail(
        subject,
        body.strip(),
        f"{sender_name} <{sender_email}>",
        [user.email],
        fail_silently=False,
    )


def generate_totp_secret():
    """
    Generate a base32 secret key for TOTP MFA (Google Authenticator, etc.).

    Returns:
        str: A base32-encoded secret string.
    """
    return pyotp.random_base32()

def generate_verification_token(user, salt="auth-token"):
    """
    Generate a time-limited token for a user using their primary key.

    Args:
        user (User): The user instance.
        salt (str): Optional salt for the serializer.

    Returns:
        str: Signed token string.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(str(user.pk), salt=salt)

def get_email_sender_details(website_id, type="notification"):
    """
    Returns the sender name, email address,
    and domain based on the email type.
    Fetches these details from the WebsiteSettings
    model specific to the website.
    """
    # Try to fetch the website settings from the database
    try:
        # Fetch the website by its ID
        website = Website.objects.get(id=website_id)
        # Assuming only one settings object per website  
        website_settings = website.settings.first()  
        if website_settings:
            sender_name = website_settings.sender_name
            sender_email = website_settings.sender_email
            domain = website.domain_url
        else:
            raise WebsiteSettings.DoesNotExist
    except Website.DoesNotExist:
        raise ValueError(f"Website with ID {website_id} does not exist.")
    except WebsiteSettings.DoesNotExist:
        raise ValueError(f"No settings found for Website with ID {website_id}.")
    
    return sender_name, sender_email, domain


# Rate limiting for OTP generation (helps avoid abuse)
def is_rate_limited(user, action, max_attempts=5, window=300):
    """
    Check if a user has exceeded rate limits for a given action.
    
    max_attempts: Maximum number of attempts allowed.
    window: Time window (in seconds) within which attempts are counted.
    """
    cache_key = f"{user.id}_{action}_attempts"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        return True
    
    # Increment the counter and set it to expire after the given window
    cache.set(cache_key, attempts + 1, timeout=window)
    return False


# OTP Functions

def generate_otp(user, expires_in=5):
    """
    Generate a 6-digit OTP and store it in the database.
    
    expires_in: Time in minutes until OTP expires (default is 5 minutes).
    """
    otp_code = ''.join(random.choices(string.digits, k=6))  # OTP is a 6-digit number
    expiration_time = timezone.now() + timedelta(minutes=expires_in)

    # Store OTP securely with expiration time (Hash OTP for security)
    otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    otp = OTP.objects.create(
        user=user,
        otp_code_hash=otp_hash,
        expiration_time=expiration_time
    )
    
    # Store the OTP with expiration time
    otp = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        expiration_time=expiration_time
    )
    
    # Return the plaintext OTP for sending
    return otp_code


def verify_otp(user, otp_code):
    """
    Verify an OTP against the stored value in the database.
    
    Returns True if OTP matches and hasn't expired, False otherwise.
    """
    otp = OTP.objects.filter(user=user).last()
    otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
    if otp and otp.otp_code_hash == otp_code and otp.expiration_time > timezone.now():
        return True
    return False


# Backup Code Functions
def generate_backup_codes(self):
    """
    Generates and stores backup codes for MFA recovery.
    """
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(5)]
    hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]  # Hash each code
    self.backup_codes = hashed_codes
    self.save()
    return codes


def use_backup_code(self, code):
    """
    Verify and remove a used backup code.
    """
    hashed_code = hashlib.sha256(code.encode()).hexdigest()
    if hashed_code in self.backup_codes:
        self.backup_codes.remove(hashed_code)
        self.save()
        return True
    return False


# Magic Link Functions

def generate_magic_link(user, expires_in=60):
    """
    Generate a unique magic link token and store it.
    
    expires_in: Time in minutes until the magic link expires (default is 60 minutes).
    """
    expiration_time = timezone.now() + timedelta(minutes=expires_in)
    token = get_random_string(64)  # Secure token generation
    magic_link = MagicLink.objects.create(
        user=user,
        token=token,
        expiration_time=expiration_time
    )
    
    return magic_link.token

def verify_magic_link(user, token):
    """
    Verify magic Link and Clean up.
    """
    try:
        magic_link = MagicLink.objects.get(user=user, token=token)
        if magic_link.expiration_time > timezone.now():
            return True
        else:
            magic_link.delete()  # Clean up expired magic link
            return False
    except MagicLink.DoesNotExist:
        return False


# Email Functions

def send_verification_code_email(user, code, website_id):
    sender_name, sender_email = get_email_sender_details(website_id)
    subject = "Verify Your Account"
    message = f"""
Hi {user.first_name},

Here's your verification code: {code}

If you didn't request this, you can safely ignore it.
"""
    send_mail(
        subject,
        message.strip(),
        f"{sender_name} <{sender_email}>",
        [user.email],
        fail_silently=False,
    )


# your email sending function

def send_magic_link_email(user, token, website_id):
    sender_name, sender_email, domain = get_email_sender_details(website_id)
    link = f"{domain}/auth/magic-link/{token}/"

    subject = "Your Magic Login Link"
    message = f"""
    Hi {user.first_name},

    Use this secure link to log in: {link}

    This link will expire in 10 minutes.
    """
    
    send_mail(
        subject,
        message.strip(),
        f"{sender_name} <{sender_email}>",
        [user.email],
        fail_silently=False,
    )


# Audit Log Utility

def log_audit_action(user, action_type, request):
    AuditLog = apps.get_model("authentication", "AuditLog")
    ip, _ = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        ip_address=ip,
        user_agent=user_agent,
        path=request.get_full_path(),
    )



# Rate Limiting with Device/IP Recognition
def is_device_rate_limited(user, action, ip, device_id, max_attempts=5, window=300):
    cache_key = f"{user.id}_{action}_{ip}_{device_id}_attempts"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= max_attempts:
        return True
    
    cache.set(cache_key, attempts + 1, timeout=window)
    return False


def log_logout_event(request, user, reason="user_initiated"):
    ip, _ = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

    LogoutEvent.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        session_key=request.session.session_key,
        reason=reason
    )


def notify_mfa_enabled(user):
    """
    Notify user that MFA has been enabled on their account.

    Args:
        user (User): The user who enabled MFA.
    """
    subject = "Multi-Factor Authentication Enabled"
    message = (
        f"Hello {user.username},\n\n"
        "You have successfully enabled MFA on your account.\n"
        "If this wasn't you, please contact support immediately.\n\n"
        "– The Security Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

def send_mfa_recovery_email(user, recovery_code):
    """
    Sends an MFA recovery email containing a one-time recovery code.

    Args:
        user (User): The user requesting MFA recovery.
        recovery_code (str): The unique recovery code to use.
    """
    subject = "Your MFA Recovery Code"
    message = (
        f"Hi {user.username},\n\n"
        "You requested a recovery code to regain access to your account.\n"
        f"Your recovery code is: {recovery_code}\n\n"
        "Use this code to disable MFA and log in. "
        "If this wasn't you, contact support immediately.\n\n"
        "– The Security Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )


def verify_email_otp(secret, otp_code):
    """
    Verifies a 6-digit OTP code against a shared TOTP secret.

    Args:
        secret (str): The base32 TOTP secret.
        otp_code (str): The OTP code entered by the user.

    Returns:
        bool: True if the code is valid, False otherwise.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=1)