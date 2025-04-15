import random
import string
import hashlib
import pyotp, qrcode
import requests
from user_agents import parse
from datetime import timedelta, datetime
from rest_framework import status
from django.core.mail import send_mail
from rest_framework.response import Response
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from .models import AuditLog
from .models import User 
from django.contrib.auth import get_user_model
from .models import AuditLog
from ipware import get_client_ip
from django.utils import timezone
from users.utils import get_client_ip 
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from websites.utils import get_primary_domain, get_email_sender_details
from django.core.mail import send_mail
from websites.utils import get_email_sender_details, get_primary_domain
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from authentication.models import AuditLog
from websites.models import Website
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.core.cache import cache


logger = logging.getLogger(__name__)
User = get_user_model()


def is_token_expired(self, token_type):
    """
    Checks whether a token has expired.
    """
    expiration_time = getattr(self, f'{token_type}_expires')
    if expiration_time and now() > expiration_time:
        return True
    return False

def impersonate_user(admin_user, target_user):
    if admin_user.has_permission('can_impersonate'):
        # Log the action
        log_audit_action(admin_user, "impersonate_user", request)
        return target_user
    raise PermissionDenied("You do not have permission to impersonate users.")


def is_rate_limited(user, action):
    cache_key = f"{user.id}_{action}_attempts"
    attempts = cache.get(cache_key, 0)
    if attempts > 5:
        return True
    cache.set(cache_key, attempts + 1, timeout=60*5)  # 5 minutes timeout
    return False

def get_website_from_request(request):
    host = request.get_host().lower()
    return Website.objects.filter(domain__icontains=host).first()

def send_mfa_recovery(user, website):
    subject = f"Recover Access to Your {website.name} Account"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    context = {
        "user": user,
        "site_name": website.name,
        "support_email": website.support_email,
        "recovery_url": f"https://{website.domain}/recover-mfa?email={user.email}"
    }

    # Render HTML and plain versions (if you have templates)
    html_message = render_to_string("emails/mfa_recovery.html", context)
    plain_message = render_to_string("emails/mfa_recovery.txt", context)

    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
        reply_to=[website.support_email],
    )


def mfa_recovery_view(request):
    user = User.objects.get(email=request.data["email"])  # example

    website = get_website_from_request(request)
    site_name = website.name if website else "Our Platform"

    send_mfa_recovery(user, site_name)
    return Response({"message": "Recovery email sent"})


def generate_mfa_qr_code(user):
    # Generate a secret key for the user
    totp = pyotp.TOTP(pyotp.random_base32())  # This will generate a base32 secret
    secret = totp.secret

    # Store the secret in your user model or a dedicated MFA model
    user.profile.mfa_secret = secret
    user.profile.save()

    # Generate the QR code URL using the secret
    uri = totp.provisioning_uri(name=user.email, issuer_name="MyApp")

    # Generate the QR code image
    img = qrcode.make(uri)
    
    # Save the image to a file-like object
    img_io = BytesIO()
    img.save(img_io)
    img_io.seek(0)
    return ContentFile(img_io.read(), name='mfa_qr_code.png')

def generate_mfa_secret():
    return pyotp.random_base32()

def verify_mfa_code(user, token):
    totp = pyotp.TOTP(user.profile.mfa_secret)
    return totp.verify(token)

def auto_detect_country(self, request):
    """
    Auto-detect user's country and timezone based on IP address.
    Only runs if not already set.
    """
    if hasattr(self, 'detected_country') and self.detected_country:
        return  # Already set

    try:
        ip_address = get_client_ip(request)
        if not ip_address:
            return

        # Example: Use ipapi.co for geolocation
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        if response.status_code == 200:
            data = response.json()
            country = data.get('country_name')
            timezone = data.get('timezone')

            if country:
                self.detected_country = country

            if timezone:
                self.detected_timezone = timezone

            self.save(update_fields=['detected_country', 'detected_timezone'])

    except Exception as e:
        # Avoid crashing — just log or silently fail
        print(f"[GeoDetection] Failed to detect country: {e}")


def custom_rate_limit_handler(request, exception):
    """Custom response when rate limit is exceeded, with retry instructions."""
    retry_after = 60  # Assume a 1-minute cooldown (adjust based on actual throttle)
    return Response(
        {
            "error": "Too many requests. Please slow down.",
            "retry_after_seconds": retry_after
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(retry_after)}
    )

def check_admin_access(user):
    """Ensures only Superadmins & Admins can manage users."""
    if user.role not in ["superadmin", "admin"]:
        raise ForbiddenAccess()
    
def get_device_info(request):
    """Detects device type (Mobile, Tablet, Desktop)."""
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    parsed_agent = parse(user_agent)

    device_type = "Desktop"
    if parsed_agent.is_mobile:
        device_type = "Mobile"
    elif parsed_agent.is_tablet:
        device_type = "Tablet"

    browser = f"{parsed_agent.browser.family} {parsed_agent.browser.version_string}"
    return f"{device_type} - {browser}"


# Helper function to verify Google reCAPTCHA
def verify_recaptcha(recaptcha_response):
    """Verifies reCAPTCHA response with Google API."""
    recaptcha_secret = settings.RECAPTCHA_SECRET_KEY
    payload = {'secret': recaptcha_secret, 'response': recaptcha_response}
    
    try:
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload, timeout=3)
        response.raise_for_status()  # Raise error for HTTP failures
        result = response.json()
        return result.get("success", False)
    except requests.RequestException as e:
        logger.error(f"reCAPTCHA verification failed: {e}")
        return False  # Fail securely if reCAPTCHA check is unavailable

 
# Account Locking
def lock_account(user, reason, duration_minutes=30):
    """Lock the account for a specified duration."""
    user.is_locked = True
    user.lock_reason = reason
    user.lock_expires_at = timezone.now() + timezone.timedelta(minutes=duration_minutes)
    user.save()

def unlock_account(user):
    """Unlock the account."""
    user.is_locked = False
    user.lock_reason = None
    user.lock_expires_at = None
    user.save()

def check_if_locked(self):
        """Checks if the account should still be locked."""
        if self.is_locked and self.lockout_until and now() > self.lockout_until:
            self.unlock_account()  # Unlock automatically after lockout period

def is_account_locked(user):
    """Check if the account is locked and whether the lock is expired."""
    if not user.is_locked:
        return False
    if user.lock_expires_at and timezone.now() > user.lock_expires_at:
        unlock_account(user)
        return False
    return True

# Failed Login Tracking (optional)
def increment_failed_attempts(user):
    """Increase the failed login attempts counter and lock the account if needed."""
    failed_attempts = user.profile.failed_login_attempts + 1
    user.profile.failed_login_attempts = failed_attempts
    user.profile.save()

    if failed_attempts >= 5:  # Or whatever your threshold is
        lock_account(user, reason="Too many failed login attempts")

def log_mfa_action(user, action, request=None):
    ip_address = None
    user_agent = "Unknown"
    if request:
        ip_address, _ = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent
    )

def logout_all_sessions(user):
    from django.contrib.sessions.models import Session
    for session in Session.objects.all():
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            session.delete()


def generate_mfa_secret(self):
        """
        Generate and assign a new MFA secret key.
        """
        secret = pyotp.random_base32()
        self.mfa_secret = secret
        self.save()
        return secret
    
def generate_totp_secret(self):
    """Generates a new TOTP secret key for Google Authenticator."""
    self.mfa_secret = pyotp.random_base32()
    self.save()
    return self.mfa_secret
    
def generate_otp_code(self):
    """Generate OTP for TOTP or email authentication."""
    if self.mfa_method == 'totp':
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.generate_otp()
    elif self.mfa_method in ['sms', 'email']:
        return str(random.randint(100000, 999999))  # 6-digit OTP
    return None
    
def get_totp_uri(self):
    """Returns the URI for configuring Google Authenticator."""
    return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(self.email, issuer_name="YourApp")
    
def verify_totp(self, token):
    """Verifies a TOTP code."""
    return pyotp.TOTP(self.mfa_secret).verify(token)
    
def generate_otp(self):
    """Generates a 6-digit OTP and sets an expiry time."""
    self.otp_code = f"{random.randint(100000, 999999)}"
    self.otp_expires_at = now() + timedelta(minutes=5)
    self.save()
    return self.otp_code

def send_email_otp(self):
    """Sends OTP via email."""
    otp = self.generate_otp()
    send_mail(
        "Your MFA OTP Code",
        f"Use this OTP to log in: {otp}",
        "no-reply@yourapp.com",
        [self.email],
        fail_silently=False,
    )

def generate_backup_codes(self):
    """
    Generates and stores backup codes for MFA recovery.
    """
    import random
    import string
    import hashlib
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
    
def generate_email_otp(self):
    """Generates a 6-digit OTP for email authentication."""
    self.otp_code = str(random.randint(100000, 999999))
    self.otp_expires_at = now() + timedelta(minutes=5)
    self.save()
    return self.otp_code

def verify_email_otp(self, otp):
    """Verifies Email OTP before expiration."""
    if self.otp_expires_at and now() > self.otp_expires_at:
        return False  # OTP Expired
    return self.otp_code == otp
    
def verify_otp(self, otp):
    """Verifies OTP before expiration."""
    if self.otp_expires_at and now() > self.otp_expires_at:
        return False  # OTP Expired
    return self.otp_code == otp
def generate_mfa_recovery_token(self):
    """
    Generate a one-time recovery token valid for 15 minutes.
    """
    self.mfa_recovery_token = get_random_string(64)
    self.mfa_recovery_expires = now() + timedelta(minutes=15)
    self.save()
    return self.mfa_recovery_token

def generate_verification_token(user):
    """
    Generate a JWT token for user email verification.
    The token will contain the user ID and an expiration time (24 hours).
    """
    expiration_time = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    payload = {
        'user_id': user.id,
        'exp': expiration_time,  # Expiration time in the payload
    }
    
    # Generate the token using the SECRET_KEY from settings
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')  # Signing with HS256 algorithm
    
    return token

def send_verification_code_email(user, code):
    sender_name, sender_email = get_email_sender_details("notification")
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

def send_magic_link_email(user, token):
    sender_name, sender_email = get_email_sender_details("notification")
    domain = get_primary_domain()
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

def decode_verification_token(token):
    """
    Decode the JWT token to get user data (e.g., user ID) and validate the token.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

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
    
def send_unlock_email(user):
    unlock_link = f"{settings.FRONTEND_URL}/unlock-account?email={user.email}"
    subject = "Unlock Your Account"
    message = f"Hi {user.get_full_name() or user.username},\n\n" \
              f"It looks like your account was locked. Click the link below to unlock it:\n\n" \
              f"{unlock_link}\n\n" \
              f"If you didn't request this, ignore the email."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def log_audit_action(user, action_type, request):
    ip, _ = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        ip_address=ip,
        user_agent=user_agent,
        path=request.get_full_path(),
    )

def impersonate_user(admin_user, target_user):
    if admin_user.has_permission('can_impersonate'):
        # Log the action
        log_audit_action(admin_user, "impersonate_user", request)
        return target_user
    raise PermissionDenied("You do not have permission to impersonate users.")


def log_sensitive_action(user, action_type, request, additional_info=None):
    ip, _ = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        ip_address=ip,
        user_agent=user_agent,
        path=request.get_full_path(),
        additional_info=additional_info
    )


def enforce_mfa(self, action):
    if self.is_mfa_enabled and action in ['login', 'account_update']:
        if not self.is_verified_via_mfa():
            raise AuthenticationFailed("MFA verification is required.")


def revoke_token(self, token_type):
    setattr(self, f'{token_type}_token', None)
    self.save()

def session_timeout(self):
    session_duration = self.get_session_duration()
    if now() - self.last_login > session_duration:
        self.logout()

def regenerate_backup_codes(self):
    if not self.backup_codes:  # If all codes have been used
        return self.generate_backup_codes()
    return []


def validate_password_strength(password):
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        raise ValidationError("Password must be at least 8 characters long and contain both letters and numbers.")

